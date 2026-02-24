import React from "react";
import { Drawer, List, ListItemButton, ListItemText, Typography } from "@mui/material";
import { useAtom } from "jotai";
import { TabHelper } from "../../atom";

const drawerWidth = 240;

export default function Sidebar() {
  const [tab] = useAtom(TabHelper.tabSelectedAtom());

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: "border-box",
          p: 3,
        },
      }}
    >
      <Typography variant="h6" fontWeight={700} color="success.main" mb={4}>
        🌿 HarmonIAgro
      </Typography>

      <List>
        {["Data Ingestion", "Semantic Mapping", "Units Alignment"].map(
          (label, index) => (
            <ListItemButton
              key={index}
              selected={tab === index}
              onClick={() => TabHelper.setTab(index)}
            >
              <ListItemText primary={label} />
            </ListItemButton>
          )
        )}
      </List>
    </Drawer>
  );
}
