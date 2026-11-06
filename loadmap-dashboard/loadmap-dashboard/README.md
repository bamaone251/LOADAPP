# Load Map Run Dashboard

Separate dashboard for your existing Load Map app. No changes to the Load Map app are required.

## Start

1. Extract this folder.
2. Set LOADMAP_URL in docker-compose.yml to your running load map app's base URL if different from https://loadmap.loxload.com. It must expose GET /api/loadmaps returning the map list, as in the attached backup source. You can use the source server's IP and port instead. Localhost inside this container is the dashboard container, not your host.
3. Run:

   docker compose up -d --build

4. Open http://YOUR-SERVER-IP:8009

To change the public port, change the left side of 8009:8009.

## Behavior

- The first visit each day asks for Runs Total. The server stores the value by Central calendar date and shares it across devices. Edit daily total lets you correct it.
- Runs Completed counts each load map whose map_date is today. Legacy records without map_date use created_at converted from UTC into Central Time. Edits do not increment the count, and multiple maps with the same run number each count once. Deleting a map removes it from the count.
- PLBs Created, Consolidations, Rebuilds, and Rewraps sum plbs_created, dpr_consolidations, dpr_rebuilds, and dpr_rewraps from today’s load maps. These are recorded totals, not separate timestamped events: the source stores no individual activity creation timestamps. They use the same map_date / legacy created_at date rule as Runs Completed.
- Refreshes every 15 seconds and rolls over at the next refresh after midnight, including while the page stays open.
- Source errors display an unavailable state rather than a false zero. The daily total can still be entered during an outage.
- A progress bar and remaining count use the same two numbers.
- ./data persists daily totals across container rebuilds. Keep this directory when updating.
- This dashboard has no login, matching the source app. Anyone who can access it can edit the daily total.

The supplied ZIP was missing a root app.py and active templates/static folders; it contained backup source. This dashboard integrates with the running application's existing API rather than attempting to reconstruct or replace it. Live connectivity must be confirmed on your server.
