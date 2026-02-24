import { Box, CssBaseline, Typography } from "@mui/material";
import { useAtom } from "jotai";
import { TabHelper } from "../atom";
import Sidebar from "./import/Sidebar";
import ImportPage from "./import/ImportPage";
import SemantiqueMappingPage from "./SemantiqueMapping/SemantiqueMapping";

export default function PageShell() {
  const [tab] = useAtom(TabHelper.tabSelectedAtom());

  return (
    <Box sx={{ display: "flex", width: "100%" }}>
      <CssBaseline />
      <Sidebar />

      <Box component="main" sx={{ flexGrow: 1, bgcolor: "grey.50", p: 5, minHeight: "100vh" }}>
        {tab === 0 && <ImportPage />}
        {tab === 1 && <SemantiqueMappingPage />}
        {tab === 2 && <Typography variant="h5">Units Alignment (Coming soon)</Typography>}
      </Box>
    </Box>
  );
}
