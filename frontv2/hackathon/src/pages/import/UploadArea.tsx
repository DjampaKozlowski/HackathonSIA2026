import React from "react";
import { Card, CardContent, Stack, Typography, Button } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { useAtom } from "jotai";
import { ImportHelper } from "../../atom";

export default function UploadArea() {
  const [, setFile] = useAtom(ImportHelper.fileAtom());

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
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
            Supports Excel (.xlsx) and PDF
          </Typography>

          <Button variant="contained" sx={{ borderRadius: 3 }}>
            Process Uploads
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
