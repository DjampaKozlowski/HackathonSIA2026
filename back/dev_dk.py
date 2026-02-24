from src.embedding.embedding import SemanticEmbedding

ref_json_toy = [
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

var_json =   {
    "dataset_id": "mysuperdataset",
    "trait_id": "SR_ROT",
    "trait": "Sour Rot",
    "method":"visual rating",
    "unit": "S1_9",
    "description": "Berry sour rot estimation (1 to 9 scale)",
    "aliases": []
  }







if __name__ == '__main__':
    semantic_embedding = SemanticEmbedding(referential_json=ref_json_toy, model_name="nomic-embed-text-v1.5")
    best_matches = semantic_embedding.get_best_matches(var_json, top_k=2)
    print(best_matches)

