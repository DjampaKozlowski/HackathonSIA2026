type TNormalizedVariable = {
    data_import_id:string;
    dataset_id:string;
    trait_id:string;
    description:string;
    method:string;
    unit:string;
    trait:string;

}
type TNormalizedVariableAPI = {
    trait_id:string;
    description:string;
    trait:string;
    method:string;
    unit:string;
}

type TReferencialVariable = {
    ref_id:string;
    name:string;
    units:string[];
    methods:string[];
    description:string;
    aliases:string[];
}

type TMappingAPI = {
    ref_id:string;
    data_import_id:string;
    score:number;
    why_description:string;
}
type TMapping = {
    id:string;
    ref_id:string;
    data_import_id:string;
    score:number;
    why_description:string;
}