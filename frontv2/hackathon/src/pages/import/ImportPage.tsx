import { Box, Typography } from "@mui/material";
import FileCard from "./FileCard";
import UploadArea from "./UploadArea";
import VariableDefinitionsTable from "./VariableDefinitionsTable";





// ============================
// Main Page
// ============================
export default function ImportPage() {
  return (
    <>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Data Ingestion
      </Typography>

      <Typography variant="body1" color="text.secondary" mb={4}>
        Upload your data files and review the extracted variables
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: 4,
          mb: 6,
        }}
      >
        <UploadArea />
        <FileCard />
      </Box>

      <VariableDefinitionsTable />
    </>
  );
}
