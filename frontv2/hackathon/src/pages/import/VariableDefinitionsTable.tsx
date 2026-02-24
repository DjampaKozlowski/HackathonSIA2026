/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Card,
  CardContent,
  Stack,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { useAtom } from "jotai";
import { ImportHelper } from "../../atom";

export default function VariableDefinitionsTable() {
  const [rows] = useAtom(ImportHelper.rowsAtom());

  const handleAdd = () => {
    ImportHelper.addRow({
      trait_id: "",
      description: "",
      method: "",
      units: "",
      dataset_id: "",
    });
  };

  const handleChange = (id: string, field: string, value: string) => {
    const row = rows.find((r: any) => r.id === id);
    if (!row) return;
    ImportHelper.updateRow(id, { ...row, [field]: value });
  };

  return (
    <Card sx={{ borderRadius: 4 }}>
      <CardContent>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={2}
        >
          <Typography variant="h6" fontWeight={600}>
            Variable Definitions
          </Typography>

          <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAdd}>
            Add Row
          </Button>
        </Stack>

        <TableContainer component={Paper} elevation={0}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Dataset ID</TableCell>
                <TableCell>Trait ID</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Method</TableCell>
                <TableCell>Units</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row: any) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <TextField
                      value={row.dataset_id}
                      onChange={(e) => handleChange(row.id, "dataset_id", e.target.value)}
                      variant="standard"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      value={row.trait_id}
                      onChange={(e) => handleChange(row.id, "trait_id", e.target.value)}
                      variant="standard"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      value={row.description}
                      onChange={(e) => handleChange(row.id, "description", e.target.value)}
                      variant="standard"
                      fullWidth
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      value={row.method}
                      onChange={(e) => handleChange(row.id, "method", e.target.value)}
                      variant="standard"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      value={row.units}
                      onChange={(e) => handleChange(row.id, "units", e.target.value)}
                      variant="standard"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton onClick={() => ImportHelper.deleteRow(row.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
