import React from "react";
import { Card, CardContent, Stack, Typography, Button } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { getDefaultStore, useAtom } from "jotai";
import { ApiHelper, ImportHelper, variableImportAtom } from "../../atom";

export default function UploadArea() {
  const [, setFile] = useAtom(ImportHelper.fileAtom());
  const [isLoading, setIsLoading] = React.useState(false);
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setIsLoading(true);
      await ApiHelper.postFile(e.target.files?.[0])
        .then((result) => {
          console.log(result.data.variables);
          getDefaultStore().set(
            variableImportAtom,
            result.data.variables.map((elt) => ({
              description: elt.description ?? "",
              method: elt.method ?? "",
              trait_id: elt.trait_id ?? "",
              unit: elt.unit ?? "",
              data_import_id: crypto.randomUUID(),
              dataset_id: e.target.files![0].name,
              trait: elt.trait ?? "",
              aliases:"",
            })),
          );
          console.log("upload complete");
        })
        .finally(() => setIsLoading(false));
    }
  };

  return (
    <Card sx={{ border: "2px dashed #c4c4c4", borderRadius: 4 }}>
      <CardContent>
        <Stack spacing={2} alignItems="center" sx={{ py: 6 }}>
          <CloudUploadIcon sx={{ fontSize: 48, color: "text.secondary" }} />

          <Typography>
            Drag & drop files here or
            <Button component="label" size="small">
              click to browse
              <input type="file" hidden onChange={handleFileChange} />
            </Button>
          </Typography>

          <Typography variant="body2" color="text.secondary">
            Supports Excel (.xlsx) and PDF {isLoading ? " - Uploading..." : ""}
          </Typography>

          <Button variant="contained" sx={{ borderRadius: 3 }}>
            Process Uploads
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
