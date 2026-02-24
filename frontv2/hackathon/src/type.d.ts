type TDataImport = {
    dataImportId:string;
    datasetId:string;
    traitID:string;
    description:string;
    method:string;
    units:string;
}

type TReferencialVariable = {
    refId:string;
    name:string;
    units:string[];
    methods:string[];
    description:string;
    aliases:string[];
}

type TMapping = {
    id:string;
    refId:string;
    dataImportId:string;
    score:number;
    whyMatch:string;
}