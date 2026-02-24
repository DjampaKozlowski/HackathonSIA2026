import { atom, getDefaultStore } from "jotai";

export const referencialVariablesAtom = atom<TReferencialVariable[]>([
  {
    refId: "ref1",
    name: "Temperature",
    units: ["°C", "K"],
    methods: ["Thermometer", "Satellite"],
    description:
      "Measure of the average kinetic energy of the particles in a system",
    aliases: ["Temp", "T"],
  },
  {
    refId: "ref2",
    name: "Poids",
    units: ["°C", "K"],
    methods: ["Thermometer", "Satellite"],
    description:
      "Measure of the average kinetic energy of the particles in a system",
    aliases: ["Temp", "T"],
  },
  {
    refId: "ref3",
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
    dataImportId: "import1",
    datasetId: "dataset1",
    traitID: "trait1",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
  {
    dataImportId: "import2",
    datasetId: "dataset1",
    traitID: "trait2",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
    {
    dataImportId: "import3",
    datasetId: "dataset1",
    traitID: "trait3",
    description: "Average temperature during the growing season",
    method: "Thermometer",
    units: "°C",
  },
]);
const importFileAtom = atom<File>();
export const matchingResultsAtom = atom<TMapping[]>([
  {
    id: crypto.randomUUID(),
    refId: "ref1",
    dataImportId: "import1",
    score: 0.8,
    whyMatch: "High similarity in description and method",
  },
  {
    id: crypto.randomUUID(),
    refId: "ref1",
    dataImportId: "import2",
    score: 0.6,
    whyMatch: "Moderate similarity in description",
  },
    {
    id: crypto.randomUUID(),
    refId: "ref2",
    dataImportId: "import3",
    score: 0.5,
    whyMatch: "Moderate similarity in description",
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
  static addRow(importData: Omit<TDataImport, "id">) {
    getDefaultStore().set(variableImportAtom, (prev) => [
      ...prev,
      { ...importData, dataImportId: crypto.randomUUID() },
    ]);
  }
  static updateRow(id: string, importData: TDataImport) {
    getDefaultStore().set(variableImportAtom, (prev) =>
      prev.map((item) => (item.dataImportId === id ? importData : item)),
    );
  }
  static deleteRow(id: string) {
    getDefaultStore().set(variableImportAtom, (prev) =>
      prev.filter((item) => item.dataImportId !== id),
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
