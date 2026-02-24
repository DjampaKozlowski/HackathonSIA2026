/* eslint-disable react-refresh/only-export-components */
/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { useMemo } from "react";
import {
  Sankey,
  Tooltip,
  ResponsiveContainer,
  Rectangle
} from "recharts";

// =============================
// Types
// =============================

export interface SourceNode {
  id: string;
  label: string;
}

export interface TargetNode {
  id: string;
  label: string;
}

export interface Relation {
  sourceId: string;
  targetId: string;
  value: number;
}

export interface SankeyChartProps {
  sources: SourceNode[];
  targets: TargetNode[];
  relations: Relation[];
  height?: number;
}

interface SankeyData {
  nodes: { name: string; type: "source" | "target" }[];
  links: { source: number; target: number; value: number }[];
}

// =============================
// Custom Node (COULEURS)
// =============================

const CustomNode = (props: any) => {
  const { x, y, width, height, payload } = props;

  const fill =
    payload.type === "source" ? "#fca5a5" : "#86efac"; // rouge clair / vert clair

  return (
    <g>
      <Rectangle x={x} y={y} width={width} height={height} fill={fill} />
      <text
        x={x + width / 2}
        y={y + height / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={12}
        fill="#1f2937"
      >
        {payload.name}
      </text>
    </g>
  );
};

// =============================
// Custom Link (COULEURS)
// =============================

const getLinkColor = (value: number): string => {
  // Exemple de logique métier :
  // faible = vert, moyen = orange, fort = rouge
  if (value < 10) return "#22c55e";     // vert
  if (value < 20) return "#f59e0b";     // orange
  return "#ef4444";                     // rouge
};

const CustomLink = (props: any) => {
  const {
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourceControlX,
    targetControlX,
    linkWidth,
    payload
  } = props;

  const strokeColor = getLinkColor(payload.value);

  return (
    <path
      d={`M${sourceX},${sourceY}
          C${sourceControlX},${sourceY}
           ${targetControlX},${targetY}
           ${targetX},${targetY}`}
      stroke={strokeColor}
      strokeWidth={linkWidth}
      fill="none"
      strokeOpacity={0.6}
    />
  );
};

// =============================
// Component
// =============================

const SankeyChart: React.FC<SankeyChartProps> = ({
  sources,
  targets,
  relations,
  height = 500
}) => {
  const data: SankeyData = useMemo(() => {
    const nodes = [
      ...sources.map((s) => ({ name: s.label, type: "source" as const })),
      ...targets.map((t) => ({ name: t.label, type: "target" as const }))
    ];

    const links = relations.map((r) => {
      const sourceIndex = sources.findIndex(
        (s) => s.id === r.sourceId
      );

      const targetIndex =
        sources.length +
        targets.findIndex((t) => t.id === r.targetId);

      return {
        source: sourceIndex,
        target: targetIndex,
        value: r.value
      };
    });

    return { nodes, links };
  }, [sources, targets, relations]);

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <Sankey
          data={data}
          nodePadding={40}
          node={<CustomNode />}
          link={<CustomLink />}
        >
          <Tooltip />
        </Sankey>
      </ResponsiveContainer>
    </div>
  );
};

export default SankeyChart;

// =============================
// DEMO DATA
// =============================

export const demoSources: SourceNode[] = [
  { id: "s1", label: "Fréquence mildiou feuille" },
  { id: "s2", label: "Surface foliaire attaquée" },
  { id: "s3", label: "Fréquence mildiou rafle" },
  { id: "s4", label: "Intensité mildiou rafle" },
  { id: "s5", label: "Poids vendange (kg)" }
];

export const demoTargets: TargetNode[] = [
  { id: "t1", label: "À créer" },
  { id: "t2", label: "Rendement par pied" }
];

export const demoRelations: Relation[] = [
  { sourceId: "s1", targetId: "t1", value: 10 },
  { sourceId: "s2", targetId: "t1", value: 15 },
  { sourceId: "s3", targetId: "t2", value: 8 },
  { sourceId: "s4", targetId: "t2", value: 12 },
  { sourceId: "s5", targetId: "t2", value: 20 }
];

export const SankeyDemo = () => {
  return (
    <SankeyChart
      sources={demoSources}
      targets={demoTargets}
      relations={demoRelations}
      height={600}
    />
  );
};
