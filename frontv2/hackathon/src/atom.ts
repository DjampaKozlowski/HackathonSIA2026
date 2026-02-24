import axios from "axios";
import { atom, getDefaultStore } from "jotai";

const HOST = "http://localhost:8000";
export const referencialVariablesAtom = atom<TReferencialVariable[]>([
  {
    ref_id: "ref1",
    name: "Temperature",
    units: ["°C", "K"],
    methods: ["Thermometer", "Satellite"],
    description:
      "Measure of the average kinetic energy of the particles in a system",
    aliases: ["Temp", "T"],
  },
  {
    ref_id: "ref2",
    name: "Poids",
    units: ["°C", "K"],
    methods: ["Thermometer", "Satellite"],
    description:
      "Measure of the average kinetic energy of the particles in a system",
    aliases: ["Temp", "T"],
  },
  {
    ref_id: "ref3",
    name: "Surface",
    units: ["°C", "K"],
    methods: ["Thermometer", "Satellite"],
    description:
      "Measure of the average kinetic energy of the particles in a system",
    aliases: ["Temp", "T"],
  },
]);
const tabSelectedAtom = atom(0); // 0: data ingestion, 1: semantic mapping, 2: units alignment
const variableImportAtom = atom<TDataImport[]>([
  {
    data_import_id: "import1",
    dataset_id: "dataset1",
    trait_id: "trait1",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
  {
    data_import_id: "import2",
    dataset_id: "dataset1",
    trait_id: "trait2",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
    {
    data_import_id: "import3",
    dataset_id: "dataset1",
    trait_id: "trait3",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
]);
const importFileAtom = atom<File>();
export const matchingResultsAtom = atom<TMapping[]>([
  {
    id: crypto.randomUUID(),
    ref_id: "ref1",
    data_import_id: "import1",
    score: 0.8,
    why_match: "High similarity in description and method",
  },
  {
    id: crypto.randomUUID(),
    ref_id: "ref1",
    data_import_id: "import2",
    score: 0.6,
    why_match: "Moderate similarity in description",
  },
    {
    id: crypto.randomUUID(),
    ref_id: "ref2",
    data_import_id: "import3",
    score: 0.5,
    why_match: "Moderate similarity in description",
  },
]);

const semanticThresholdAtom = atom(0.65);

export class TabHelper {
  static setTab(index: number) {
    getDefaultStore().set(tabSelectedAtom, index);
  }
  static tabSelectedAtom() {
    return tabSelectedAtom;
  }
}
export class ImportHelper {
  static addRow(importData: Omit<TDataImport, "data_import_id">) {
    getDefaultStore().set(variableImportAtom, (prev) => [
      ...prev,
      { ...importData, data_import_id: crypto.randomUUID() },
    ]);
  }
  static updateRow(id: string, importData: TDataImport) {
    getDefaultStore().set(variableImportAtom, (prev) =>
      prev.map((item) => (item.data_import_id === id ? importData : item)),
    );
  }
  static deleteRow(id: string) {
    getDefaultStore().set(variableImportAtom, (prev) =>
      prev.filter((item) => item.data_import_id !== id),
    );
  }
  static fileAtom() {
    return importFileAtom;
  }

  static rowsAtom() {
    return variableImportAtom;
  }
}

export class SemantiqueMappingHelper {
  static thresholdAtom() {
    return semanticThresholdAtom;
  }

  static mappingsAtom() {
    return matchingResultsAtom;
  }

  static setThreshold(value: number) {
    getDefaultStore().set(semanticThresholdAtom, value);
  }

  static removeMapping(id: string) {
    getDefaultStore().set(matchingResultsAtom, (prev) =>
      prev.filter((m) => m.id !== id),
    );
  }

  static setMappings(mappings: TMapping[]) {
    getDefaultStore().set(matchingResultsAtom, mappings);
  }
}


export class ApiHelper {
  private static getReference() {
    return axios.get<{items:TReferencialVariable[],count:number}>(`${HOST}/core`);
  }

  static async loadReference() {
    await this.getReference().then((response) => {
      const data = response.data;
      getDefaultStore().set(referencialVariablesAtom, data.items);
    })
  }

  static async postFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return axios.post(`${HOST}/uploadfile`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  }

  static async getMapping() {
    return axios.get<TMapping[]>(`${HOST}/mapping`);
  }
}