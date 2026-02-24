import lmstudio as lms
from pathlib import Path
from typing import List, Union, Tuple
import numpy as np
import pandas as pd

from src.classes import ReferenceConcept, NormalizedVariable, AlignmentScore







def load_embedding_model(model_name:str = "nomic-embed-text-v1.5"):
    try:
        return lms.embedding_model(model_name)
    except Exception as e:
        print(f"Error while loading the embedding model: {e}")
        raise 
    

# def build_referential_embedding_string(entry: dict) -> str:
#     """
#     Build a structured embedding string for a referential entry.
#     Designed for semantic similarity (retrieval).
#     """

#     name = (entry.get("name") or "").strip()
#     description = (entry.get("description") or "").strip()

#     # Some descriptions contain "|" separators → normalize
#     if "|" in description:
#         description = "; ".join(
#             part.strip() for part in description.split("|") if part.strip()
#         )

#     units = entry.get("units") or []
#     methods = entry.get("methods") or []
#     aliases = entry.get("aliases") or []

#     return (
#         f"TRAIT: {name}\n"
#         f"DESCRIPTION: {description}\n"
#         f"UNITS: {', '.join(units)}\n"
#         f"METHODS: {', '.join(methods)}\n"
#         f"ALIASES: {', '.join(aliases)}"
#     ).strip()

def build_referential_embedding_string(entry: dict) -> str:
    """
    Build a structured embedding string for a referential entry.
    Designed for semantic similarity (retrieval).
    """

    name = (entry.name or "").strip()
    description = (entry.description or "").strip()

    # Some descriptions contain "|" separators → normalize
    # Some descriptions contain "|" separators → normalize
    if "|" in description:
        description = "; ".join(
            part.strip() for part in description.split("|") if part.strip()
        )

    units = entry.units or []
    methods = entry.methods or []
    aliases = entry.aliases or []

    return (
        f"TRAIT: {name}\n"
        f"DESCRIPTION: {description}\n"
        f"UNITS: {', '.join(units)}\n"
        f"METHODS: {', '.join(methods)}\n"
        f"ALIASES: {', '.join(aliases)}"
    ).strip()


# def build_dataset_embedding_string(entry: dict) -> str:
#     """
#     Build a structured embedding string for a dataset variable
#     to be matched against the referential.
#     """

#     name = (entry.get("trait") or entry.get("trait_id") or "").strip()
#     description = (entry.get("description") or "").strip()

#     unit = (entry.get("unit") or "").strip()
#     method = (entry.get("method") or "").strip()
#     aliases = entry.get("aliases") or []

#     return (
#         f"TRAIT: {name}\n"
#         f"DESCRIPTION: {description}\n"
#         f"UNITS: {unit}\n"
#         f"METHODS: {method}\n"
#         f"ALIASES: {', '.join(aliases)}"
#     ).strip()

def build_dataset_embedding_string(entry: dict) -> str:
    """
    Build a structured embedding string for a dataset variable
    to be matched against the referential.
    """

    name = (entry.trait or "").strip()
    description = (entry.description or "").strip()
    unit = (entry.unit or "").strip()
    method = (entry.method or "").strip()
    aliases = (entry.aliases or "").strip()

    return (
        f"TRAIT: {name}\n"
        f"DESCRIPTION: {description}\n"
        f"UNITS: {unit}\n"
        f"METHODS: {method}\n"
        f"ALIASES: {', '.join(aliases)}"
    ).strip()


def build_referential_embedding(
    model,
    ref_json: List[ReferenceConcept],
) -> Tuple[List[str], np.ndarray]:
    """
    Build embeddings for a referential dataset.

    Parameters
    ----------
    model : EmbeddingModel
        Model implementing an `embed(texts: Sequence[str]) -> np.ndarray`
        method. The method must return a 2D numpy array of shape (N, D).
    ref_json : Sequence[ReferenceConcept]
        Referential entries used to generate embeddings.
        Each entry must provide at least one of:
        - 'ref_id'
        - 'name'

    Returns
    -------
    Tuple[List[str], np.ndarray]
        - ref_ids: List of stable referential IDs (length N)
        - ref_embeddings: Embedding matrix of shape (N, D)

    Raises
    ------
    ValueError
        If some entries are missing both 'ref_id' and 'name'.
        If embeddings and IDs lengths mismatch.
    """

    # Build textual representation
    ref_texts: List[str] = [
        build_referential_embedding_string(r) for r in ref_json
    ]

    # Prefer stable IDs from the referential itself
    ref_ids: List[str] = [
        (entry.get("ref_id") or entry.get("name") or "").strip()
        for entry in ref_json
    ]

    if any(not rid for rid in ref_ids):
        raise ValueError(
            "Some referential entries are missing both 'ref_id' and 'name'."
        )

    # Batch embedding
    ref_embeddings: np.ndarray = model.embed(ref_texts)

    # Validation
    if len(ref_embeddings) != len(ref_ids):
        raise ValueError(
            "ref_embeddings and ref_ids must have the same length."
        )

    return ref_ids, ref_embeddings

def build_referential_embedding(
    model,
    ref_json: List[ReferenceConcept],
) -> Tuple[List[str], np.ndarray]:
    """
    Build embeddings for a referential dataset.

    Parameters
    ----------
    model : EmbeddingModel
        Model implementing an `embed(texts: Sequence[str]) -> np.ndarray`
        method. The method must return a 2D numpy array of shape (N, D).
    ref_json : Sequence[ReferenceConcept]
        Referential entries used to generate embeddings.
        Each entry must provide at least one of:
        - 'ref_id'
        - 'name'

    Returns
    -------
    Tuple[List[str], np.ndarray]
        - ref_ids: List of stable referential IDs (length N)
        - ref_embeddings: Embedding matrix of shape (N, D)

    Raises
    ------
    ValueError
        If some entries are missing both 'ref_id' and 'name'.
        If embeddings and IDs lengths mismatch.
    """

    # Build textual representation
    ref_texts: List[str] = [
        build_referential_embedding_string(r) for r in ref_json
    ]

    # Prefer stable IDs from the referential itself
    ref_ids: List[str] = [(entry.ref_id or entry.name).strip() for entry in ref_json]


    if any(not rid for rid in ref_ids):
        raise ValueError(
            "Some referential entries are missing both 'ref_id' and 'name'."
        )

    # Batch embedding
    ref_embeddings: np.ndarray = model.embed(ref_texts)

    # Validation
    if len(ref_embeddings) != len(ref_ids):
        raise ValueError(
            "ref_embeddings and ref_ids must have the same length."
        )

    return ref_ids, ref_embeddings




def save_referential_embedding(
    ref_embeddings: np.ndarray,
    ref_ids: List[str],
    dir: Union[str, Path] = ".",
    embeddings_filename: str = "ref_embeddings.npy",
    ids_filename: str = "ref_ids.npy",
) -> tuple[Path, Path]:
    """
    Save referential embeddings and their aligned IDs.

    Parameters
    ----------
    ref_embeddings : np.ndarray
        Embedding matrix of shape (N, D)
    ref_ids : Sequence
        IDs aligned with rows of ref_embeddings (length N)
    dir : str | Path
        Target directory for saving files
    embeddings_filename : str
        Filename for embeddings
    ids_filename : str
        Filename for ids

    Returns
    -------
    tuple[Path, Path]
        Paths of saved embeddings and ids files
    """

    try:


        # Resolve directory
        save_dir = Path(dir).resolve()

        # File paths
        ref_embeddings_path = save_dir / embeddings_filename
        ref_ids_path = save_dir / ids_filename

        # Save (aligned order preserved)
        np.save(ref_embeddings_path, ref_embeddings)
        np.save(ref_ids_path, np.array(ref_ids, dtype=object))

        print(f"Referential embeddings saved to: {ref_embeddings_path}")
        print(f"Referential IDs saved to: {ref_ids_path}")

        return ref_embeddings_path, ref_ids_path

    except Exception as e:
        print(f"Error during referential embedding saving: {e}")
        raise


def load_referential_embedding(
    dir: Union[str, Path] = ".",
    embeddings_filename: str = "ref_embeddings.npy",
    ids_filename: str = "ref_ids.npy"
    ):
    try:
      # Resolve directory
      save_dir = Path(dir).resolve()

      # File paths
      ref_embeddings_path = save_dir / embeddings_filename
      ref_ids_path = save_dir / ids_filename

      # Save (aligned order preserved)
      ref_embeddings = np.load(ref_embeddings_path)
      ref_ids = np.load(ref_ids_path)
      return ref_ids, ref_embeddings
    except Exception as e:
        print(f"Error while loading reference embedding: {e}")
        raise


def build_var_embedding(model, norm_var: NormalizedVariable)-> np.array:
    try:
        embedding_str = build_dataset_embedding_string(norm_var)
        return model.embed(embedding_str)
    except Exception as e:
        print(f"Error while embedding the variable content: {e}")
        raise


def get_semantic_similarity_score(var_embedding, refs_embedding) -> List[float]:
    try:
        return refs_embedding @ var_embedding
    except Exception as e:
        print(f"Error while computing semantic similarity score between the variable and the reference: {e}")
        raise

def compute_similarity(
    var_embedding: np.ndarray,
    ref_embeddings: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between a query embedding and a set of reference embeddings.

    Parameters
    ----------
    var_embedding : np.ndarray
        Shape (d,)
    ref_embeddings : np.ndarray
        Shape (n, d)
    top_k : Optional[int]
        If provided, return only the top_k most similar embeddings.

    Returns
    -------
    similarities : np.ndarray
        Cosine similarity scores.
    indices : np.ndarray
        Indices sorted by descending similarity.
    """
    try:
      # Convert to numpy if needed
      var_embedding = np.asarray(var_embedding)
      ref_embeddings = np.asarray(ref_embeddings)

      # Ensure correct shape
      if var_embedding.ndim != 1:
          raise ValueError("query_embedding must be 1D (shape: (d,))")

      if ref_embeddings.ndim != 2:
          raise ValueError("ref_embeddings must be 2D (shape: (n, d))")

      # Normalize embeddings (important for cosine similarity)
      query_norm = var_embedding / np.linalg.norm(var_embedding)
      ref_norm = ref_embeddings / np.linalg.norm(ref_embeddings, axis=1, keepdims=True)

      # Cosine similarity (vectorized dot product)
      return ref_norm @ query_norm
    except Exception as e:
      print(f"Error while computing semantic similarity score between the variable and the reference: {e}")
      raise



    
def select_k_best_match(ref_ids: List[str], similarity_scores: np.ndarray, top_k:int = 5) -> Tuple[List[AlignmentScore], List[int]]:
  try:
    # Sort descending
    idx = np.argsort(-similarity_scores)
    if top_k is not None:
        res = []
        for i in idx[:top_k]:
            res.append({"ref_id": ref_ids[i],"scores": similarity_scores[i]})
    return res, idx[:top_k]
  except Exception as e:
    print(f"Error while selection best matches with referential: {e}")


class SemanticEmbedding:
    def __init__(self, referential_json: List[ReferenceConcept], model_name:str = "nomic-embed-text-v1.5"):
      self.model = load_embedding_model(model_name=model_name)
      print("this is my model", self.model)
      self.ref_ids, self.ref_embeddings = build_referential_embedding(self.model, referential_json)   

    def get_best_matches(self, var_json: NormalizedVariable, top_k:int = 5) -> List[AlignmentScore]:   
      var_embedding = build_var_embedding(self.model, var_json)
      similarity_scores = compute_similarity(var_embedding, self.ref_embeddings)
      return select_k_best_match(self.ref_ids, similarity_scores, top_k= top_k)

