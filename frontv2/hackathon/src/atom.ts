import axios from "axios";
import { atom, getDefaultStore } from "jotai";

const HOST = "http://localhost:8000";
export const referencialVariablesAtom = atom<TReferencialVariable[]>([
  
]);
const tabSelectedAtom = atom(0); // 0: data ingestion, 1: semantic mapping, 2: units alignment
export const variableImportAtom = atom<TNormalizedVariable[]>([

]);
const importFileAtom = atom<File>();
export const matchingResultsAtom = atom<TMapping[]>([
 
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
  static addRow(importData: Omit<TNormalizedVariable, "data_import_id">) {
    getDefaultStore().set(variableImportAtom, (prev) => [
      ...prev,
      { ...importData, data_import_id: crypto.randomUUID() },
    ]);
  }
  static updateRow(id: string, importData: TNormalizedVariable) {
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
  static addMappings(mapping: TMapping[]) {
    getDefaultStore().set(matchingResultsAtom, (prev) => [...prev, ...mapping]);
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
    return axios.post<{variables:TNormalizedVariableAPI[]}>(`${HOST}/uploadfile`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  }

  static async getMapping(variable: TNormalizedVariable) {
    return axios.post<{items:TMappingAPI[]}>(`${HOST}/align`, {...variable,aliases:""});
  }
}