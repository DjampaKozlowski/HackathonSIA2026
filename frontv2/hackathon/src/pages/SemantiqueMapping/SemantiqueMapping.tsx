import React, { useEffect } from "react";
import {
  Box,
  Typography,
  Slider,
  Stack,
  IconButton,
  Paper,
} from "@mui/material";
import { alpha, useTheme } from "@mui/material/styles";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import CategoryOutlinedIcon from "@mui/icons-material/CategoryOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { getDefaultStore, useAtom } from "jotai";
import {
  ApiHelper,
  ImportHelper,
  SemantiqueMappingHelper,
  referencialVariablesAtom,
  variableImportAtom,
} from "../../atom";

function Pill({
  icon,
  label,
  score,
  variant,
  onRemove,
}: {
  icon: React.ReactNode;
  label: string;
  score?: number;
  variant: "left" | "right";
  onRemove?: () => void;
}) {
  const theme = useTheme();
  const isLeft = variant === "left";
  const borderColor = isLeft
    ? theme.palette.primary.light
    : theme.palette.success.light;
  const bgColor = isLeft
    ? alpha(theme.palette.primary.light, 0.08)
    : alpha(theme.palette.success.light, 0.1);
  const textColor = isLeft
    ? theme.palette.primary.main
    : theme.palette.success.main;

  return (
    <Paper
      elevation={0}
      sx={{
        position: "relative",
        borderRadius: 999,
        px: 2.5,
        py: 1.4,
        border: "1px solid",
        borderColor,
        bgcolor: bgColor,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 2,
        minHeight: 56,
      }}
    >
      <Stack
        direction="row"
        spacing={1.25}
        alignItems="center"
        sx={{ minWidth: 0 }}
      >
        <Box
          sx={{
            width: 34,
            height: 34,
            borderRadius: 999,
            display: "grid",
            placeItems: "center",
            bgcolor: alpha(textColor, 0.1),
            color: textColor,
            flex: "0 0 auto",
          }}
        >
          {icon}
        </Box>

        <Typography
          sx={{
            color: textColor,
            fontWeight: 600,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            maxWidth: 340,
          }}
        >
          {label}
        </Typography>
      </Stack>

      {typeof score === "number" && (
        <Typography sx={{ color: theme.palette.primary.main, fontWeight: 700 }}>
          {score.toFixed(2)}
        </Typography>
      )}

      {onRemove && (
        <IconButton
          size="small"
          onClick={onRemove}
          sx={{
            position: "absolute",
            right: -10,
            top: "50%",
            transform: "translateY(-50%)",
            bgcolor: alpha(theme.palette.error.main, 0.12),
            color: theme.palette.error.main,
            border: "1px solid",
            borderColor: alpha(theme.palette.error.main, 0.25),
            "&:hover": {
              bgcolor: alpha(theme.palette.error.main, 0.18),
            },
          }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      )}
    </Paper>
  );
}

type MappingLinesProps = {
  imports: TNormalizedVariable[];
  refs: TReferencialVariable[];
  mappings: TMapping[];
  threshold: number;
};

function MappingLines({
  imports,
  refs,
  mappings,
  threshold,
}: MappingLinesProps) {
  const theme = useTheme();
  const rowHeight = 73; // must roughly match pill height + spacing

  const importIndex = new Map<string, number>();
  imports.forEach((imp, index) => importIndex.set(imp.data_import_id, index));

  const refIndex = new Map<string, number>();
  refs.forEach((ref, index) => refIndex.set(ref.ref_id, index));

  const validMappings = mappings.filter((m) => {
    const hasImport = importIndex.has(m.data_import_id);
    const hasRef = refIndex.has(m.ref_id);
    if (!hasImport || !hasRef) {
      console.warn("Mapping ignored because it references missing entities", {
        mappingId: m.id,
        dataImportId: m.data_import_id,
        refId: m.ref_id,
      });
    }
    return hasImport && hasRef;
  });

  const maxRows = Math.max(imports.length, refs.length);
  const height = Math.max(1, maxRows) * rowHeight;

  return (
    <Box sx={{ position: "relative", height }}>
      <svg width="100%" height={height} style={{ overflow: "visible" }}>
        {validMappings.map((m) => {
          const fromIndex = importIndex.get(m.data_import_id)!;
          const toIndex = refIndex.get(m.ref_id)!;
          const y1 = (fromIndex + 0.5) * rowHeight;
          const y2 = (toIndex + 0.5) * rowHeight;
          const isAbove = m.score >= threshold;
          const color = isAbove
            ? theme.palette.success.main
            : theme.palette.grey[400];

          return (
            <path
              key={m.id}
              d={`M 10 ${y1} C 70 ${y1} 70 ${y2} 130 ${y2}`}
              stroke={color}
              strokeWidth={2}
              fill="none"
            />
          );
        })}
      </svg>
    </Box>
  );
}

export default function SemantiqueMappingPage() {
  const theme = useTheme();
  const [threshold, setThreshold] = useAtom(
    SemantiqueMappingHelper.thresholdAtom(),
  );
  const [mappings] = useAtom(SemantiqueMappingHelper.mappingsAtom());
  const [imports] = useAtom(ImportHelper.rowsAtom());
  const [referencialVariables] = useAtom(referencialVariablesAtom);

  const validMappings = React.useMemo(() => {
    const importIds = new Set(imports.map((i) => i.data_import_id));
    const refIds = new Set(referencialVariables.map((r) => r.ref_id));

    return mappings.filter((m) => {
      const ok = importIds.has(m.data_import_id) && refIds.has(m.ref_id);
      if (!ok) {
        console.warn("Mapping ignored because it references missing entities", {
          mappingId: m.id,
          dataImportId: m.data_import_id,
          refId: m.ref_id,
        });
      }
      return ok;
    });
  }, [mappings, imports, referencialVariables]);

  const bestScoreByImportId = React.useMemo(() => {
    const map = new Map<string, number>();
    validMappings.forEach((m) => {
      const prev = map.get(m.data_import_id) ?? 0;
      if (m.score > prev) {
        map.set(m.data_import_id, m.score);
      }
    });
    return map;
  }, [validMappings]);

  const mappedRefIds = React.useMemo(() => {
    const s = new Set<string>();
    validMappings.forEach((m) => s.add(m.ref_id));
    return s;
  }, [validMappings]);

  const orderedRefs = React.useMemo(() => {
    const mapped: TReferencialVariable[] = [];
    const unmapped: TReferencialVariable[] = [];
    referencialVariables.forEach((ref) => {
      if (mappedRefIds.has(ref.ref_id)) mapped.push(ref);
      else unmapped.push(ref);
    });
    return [...mapped, ...unmapped];
  }, [referencialVariables, mappedRefIds]);

  const handleRemoveForImport = (dataImportId: string) => {
    SemantiqueMappingHelper.setMappings(
      mappings.filter((m) => m.data_import_id !== dataImportId),
    );
  };

  useEffect(() => {
    ApiHelper.loadReference();
  }, []);
  useEffect(() => {
    async function load() {
      for (const v of getDefaultStore().get(variableImportAtom)) {
        console.log("Loading mappings for", v.data_import_id);
        const res = await ApiHelper.getMapping(v);
        console.log(res.data);
        SemantiqueMappingHelper.addMappings(
          res.data.items.map((elt) => ({ ...elt, id: crypto.randomUUID(),data_import_id:v.data_import_id })),
        );
      }
    }
    load();
  }, []);

  return (
    <Box sx={{ width: "100%" }}>
      <Box sx={{ maxWidth: 1100, mx: "auto" }}>
        <Stack
          spacing={1}
          alignItems="center"
          sx={{ textAlign: "center", mb: 5 }}
        >
          <Typography
            variant="h3"
            fontWeight={800}
            sx={{ letterSpacing: -0.5 }}
          >
            Semantic Schema Mapper
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Map your raw dataset variables to core standardized definitions
          </Typography>
        </Stack>

        <Stack spacing={1} alignItems="center" sx={{ mb: 5 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body1" fontWeight={600} color="text.secondary">
              Score threshold
            </Typography>
            <Box
              sx={{
                px: 1.5,
                py: 0.5,
                borderRadius: 2,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                color: theme.palette.primary.main,
                fontWeight: 800,
                minWidth: 56,
                textAlign: "center",
              }}
            >
              {threshold.toFixed(2)}
            </Box>
          </Stack>

          <Box sx={{ width: 320 }}>
            <Slider
              value={threshold}
              min={0}
              max={1}
              step={0.01}
              onChange={(_, v) => setThreshold(v as number)}
            />
          </Box>
        </Stack>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "1fr 140px 1fr",
            alignItems: "center",
            gap: 2,
            mb: 2,
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{ color: "text.secondary", fontWeight: 800, letterSpacing: 1 }}
          >
            DATASET VARIABLES
          </Typography>
          <Box />
          <Typography
            variant="subtitle2"
            sx={{ color: "text.secondary", fontWeight: 800, letterSpacing: 1 }}
          >
            CORE REFERENTIAL SCHEMA
          </Typography>
        </Box>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "1fr 140px 1fr",
            alignItems: "flex-start",
            gap: 2,
          }}
        >
          <Stack spacing={2}>
            {imports.map((imp) => (
              <Pill
                key={imp.data_import_id}
                variant="left"
                icon={<StorageOutlinedIcon fontSize="small" />}
                label={imp.trait_id || imp.data_import_id}
                score={bestScoreByImportId.get(imp.data_import_id)}
                onRemove={() => handleRemoveForImport(imp.data_import_id)}
              />
            ))}
          </Stack>

          <MappingLines
            imports={imports}
            refs={orderedRefs}
            mappings={validMappings}
            threshold={threshold}
          />

          <Stack spacing={2}>
            {orderedRefs.map((ref) => (
              <Pill
                key={ref.ref_id}
                variant="right"
                icon={<CategoryOutlinedIcon fontSize="small" />}
                label={ref.name}
              />
            ))}
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}
