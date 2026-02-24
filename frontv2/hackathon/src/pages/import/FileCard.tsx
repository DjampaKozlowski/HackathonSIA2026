import React from "react";
import { Card, CardContent, Typography, IconButton, Stack } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { useAtom } from "jotai";
import { ImportHelper } from "../../atom";

export default function FileCard() {
  const [file, setFile] = useAtom(ImportHelper.fileAtom());

  const clearFile = () => setFile(undefined as any);

  return (
    <Card sx={{ borderRadius: 4 }}>
      <CardContent>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          Uploaded file
        </Typography>

        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="body2" color="text.secondary">
            {file ? file.name : "Aucun fichier sélectionné"}
          </Typography>
          {file && (
            <IconButton size="small" onClick={clearFile}>
              <CloseIcon fontSize="small" />
            </IconButton>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
