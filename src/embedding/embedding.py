import lmstudio as lms
from pathlib import Path
import numpy as np
import pandas as pd

from src.classes import ReferenceConcept, NormalizedVariable

referential = [
  {
    "ref_id": "ref_1",
    "name": "Alcohol content",
    "units": [
      "%v/v",
    ],
    "methods": [
      "Alcohol_NIRS_analyser",
    ],
    "description": "Alcohol content",
    "aliases": [
      "ALC_C",
    ]
  },
  {
    "ref_id": "ref_2",
    "name": "Potassium concentration",
    "units": [
      "mg/l",
      "g/100g"
    ],
    "methods": [
      "HPLC ion exchange",
      "flame spec"
    ],
    "description": "Potassium concentration of the berries (IC-HPLC, mg/l)|Potassium concentration in the berries (flame spec., mg/l)|Potassium concentration in green berries (IC-HPLC, mg/l)|Must Potassium concentration (flame spec.)|Potassium concentration of the must (IC-HPLC, mg/l)|Potassium concentration in petioles (ICP-AES, g/100g)|Wine Potassium concentration",
    "aliases": [
      "BER_K_HPLC",
      "BERRY_K",
      "GBER_K",
      "MUST_K",
      "MUST_K_IC",
      "PET_K",
      "WINE_K"
    ]
  },
  {
    "ref_id": "ref_3",
    "name": "malic acid concentration",
    "units": [
      "g/l",
      "meq/l"
    ],
    "methods": [
      "Mal_Enzymatic",
      "meq/l",
      "g/l",
    ],
    "description": "Malic acid concentration of the berries (Enzym., g/l)|Malic acid concentration of the berries (HPLC, g/l)|Tartaric acid concentration in the berries (Metav.., g/l)|Tartaric acid concentration in the berries (HPLC, g/l)|Malic acid concentration in the berries (Enzym., meq/l)|Tartaric acid concentration in the berries (Metavan., meq/l)|Malic acid concentration in green berries (Enzym., g/l)|Malic acid concentration of the must (Cap. electro., g/l)|Malic acid concentration of the must (Enzym., g/l)|Malic acid concentration of the must (HPLC, g/l)|Must Malic acid concentration|Wine Malic acid concentration|Malic acid concentration in the wine (Cap. electro., g/l)",
    "aliases": [
      "BER_MAL_g",
      "BER_MAL_HPLC",
      "BERRY_MAL_meq",
      "GBER_MAL_ENZ_g",
      "MUST_MAL_CapI_g",
      "MUST_MAL_g",
      "MUST_MAL_HPLC_g",
      "MUST_MAL_meq",
      "WINE_MAL",
      "WINE_MAL_CapE_g"
    ]
  },
  {
    "ref_id": "ref_4",
    "name": "Sour rot",
    "units": [
      "S1_9",
      "%"
    ],
    "methods": [
      "Visual rating",
      "%"
    ],
    "description": "Berry sour rot estimation (1 to 9 scale)|Percentage of berries with sour rot",
    "aliases": [
      "BER_SOUR_ROT_1_9",
      "BER_SOUR_TOT_PC"
    ]
  },
]

tests =   [{
    "dataset_id": "mysuperdataset",
    "trait_id": "SR_ROT",
    "trait": "Sour Rot",
    "method":"visual rating",
    "unit": "S1_9",
    "description": "Berry sour rot estimation (1 to 9 scale)",
    "aliases": []
  }
]





def load_embedding_model(model_name:str = "nomic-embed-text-v1.5"):
    try:
        return lms.embedding_model("nomic-embed-text-v1.5")
    except Exception as e:
        raise e
    

def build_referential_embedding_string(entry: dict) -> str:
    """
    Build a structured embedding string for a referential entry.
    Designed for semantic similarity (retrieval).
    """

    name = (entry.get("name") or "").strip()
    description = (entry.get("description") or "").strip()

    # Some descriptions contain "|" separators → normalize
    if "|" in description:
        description = "; ".join(
            part.strip() for part in description.split("|") if part.strip()
        )

    units = entry.get("units") or []
    methods = entry.get("methods") or []
    aliases = entry.get("aliases") or []

    return (
        f"TRAIT: {name}\n"
        f"DESCRIPTION: {description}\n"
        f"UNITS: {', '.join(units)}\n"
        f"METHODS: {', '.join(methods)}\n"
        f"ALIASES: {', '.join(aliases)}"
    ).strip()


def build_dataset_embedding_string(entry: dict) -> str:
    """
    Build a structured embedding string for a dataset variable
    to be matched against the referential.
    """

    name = (entry.get("trait") or entry.get("trait_id") or "").strip()
    description = (entry.get("description") or "").strip()

    unit = (entry.get("unit") or "").strip()
    method = (entry.get("method") or "").strip()
    aliases = entry.get("aliases") or []

    return (
        f"TRAIT: {name}\n"
        f"DESCRIPTION: {description}\n"
        f"UNITS: {unit}\n"
        f"METHODS: {method}\n"
        f"ALIASES: {', '.join(aliases)}"
    ).strip()


def build_or_load_referential_embedding(model, referential: ReferenceConcept):
    """
    
    """
    ref_embeddings_path = Path("ref_embeddings.npy")
    ref_ids_path = Path("ref_ids.npy")  # stores IDs aligned with rows of ref_embeddings

    try:
        # Ref. Embedding (+ IDs)
        if ref_embeddings_path.exists() and ref_ids_path.exists():
            print("Ref. embedding + ids files already exist. Loading")
            ref_embeddings = np.load(ref_embeddings_path)
            ref_ids = np.load(ref_ids_path, allow_pickle=True).tolist()  # list[str]

            # Safety check: keep alignment consistent
            if len(ref_ids) != ref_embeddings.shape[0]:
                raise ValueError(
                    f"Mismatch between embeddings rows ({ref_embeddings.shape[0]}) "
                    f"and ref_ids length ({len(ref_ids)}). Delete cache files and recompute."
                )
        else:
            print("Ref. embedding file(s) not found. Ref. embedding will be computed.")
            ref_texts = [build_referential_embedding_string(r) for r in referential]

            # Prefer stable IDs from the referential itself
            ref_ids = [(entry.get("ref_id") or entry.get("name") or "").strip() for entry in referential]
            if any(not rid for rid in ref_ids):
                raise ValueError("Some referential entries are missing both 'ref_id' and 'name'.")

            ref_embeddings = model.embed(ref_texts)  # batch

            # Save embeddings + ids (same order!)
            np.save(ref_embeddings_path, ref_embeddings)
            np.save(ref_ids_path, np.array(ref_ids, dtype=object))
        return (ref_ids, ref_embeddings)
    except Exception as e:
        raise(e)



def get_embedding_match_with_referential(model, dataset:NormalizedVariable):
    try:
        text = build_dataset_embedding_string(t)
        return model.embed(test_text)
    except Exception as e:
        raise(e)
    







if __name__== "__main__":
    model = load_embedding_model()
    




    # Variables
    for t in tests:
        test_text = build_dataset_embedding_string(t)
        test_embedding = model.embed(test_text)
        # Similarity
        scores = ref_embeddings @ test_embedding

    df = pd.DataFrame(
        {
            "ref_id": [entry.get("ref_id") for entry in referential],
            "name": [entry.get("name") for entry in referential],
            "scores": scores
        }
    )

    res = (
        df
        .sort_values(by='scores', ascending=False)
        .head(2)
        [['ref_id', 'scores']]
        .to_dict(orient='records')
    )
    # print(res[['ref_id', 'scores']].to_dict(orient='records'))
    print(res)

    


        # # Optional: human-readable mapping file (tsv)
        # with open("ref_id_to_name.tsv", "w", encoding="utf-8") as f:
        #     f.write("ref_id\tname\scores\n")
        #     for i, entry in enumerate(referential):
        #         rid = (entry.get("ref_id") or entry.get("name") or "").strip()
        #         name = (entry.get("name") or "").strip()
        #         f.write(f"{rid}\t{name}\t{scores[i]}\n")
        
    



