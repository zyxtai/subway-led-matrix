"""Inspect live MTA subway predictions on a Mac; this is not a proxy server."""
import argparse
import datetime as dt
import json
import math
import sys
import time
import urllib.request

from google.transit import gtfs_realtime_pb2

BASE = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2F"
FEEDS = {"ace": "gtfs-ace", "bdfm": "gtfs-bdfm", "nqrw": "gtfs-nqrw"}


def inspect(data, stop_ids, routes, now):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)
    if not feed.IsInitialized():
        raise ValueError("Incomplete GTFS-Realtime message")
    if feed.header.incrementality != 0:
        raise ValueError("Differential feeds are not supported")
    if not feed.header.HasField("timestamp"):
        raise ValueError("Feed has no freshness timestamp")
    age = now - feed.header.timestamp
    if age > 180 or age < -60:
        raise ValueError("Feed timestamp outside freshness window: age {} seconds".format(age))
    arrivals = {}
    for entity in feed.entity:
        if entity.is_deleted or not entity.HasField("trip_update"):
            continue
        update = entity.trip_update
        trip = update.trip
        if trip.route_id not in routes or trip.schedule_relationship in (3, 7):
            continue  # CANCELED or DELETED
        for stop in update.stop_time_update:
            if stop.stop_id not in stop_ids or stop.schedule_relationship in (1, 2):
                continue  # SKIPPED or NO_DATA
            if not stop.HasField("arrival") or not stop.arrival.HasField("time"):
                continue  # Do not silently present departure times as arrivals.
            timestamp = stop.arrival.time
            if timestamp < now:
                continue
            key = (trip.trip_id, stop.stop_id)
            arrivals[key] = {
                "route": trip.route_id,
                "stop_id": stop.stop_id,
                "trip_id": trip.trip_id,
                "arrival_unix": timestamp,
                "arrival_utc": dt.datetime.fromtimestamp(timestamp, dt.timezone.utc).isoformat(),
                "minutes": math.ceil((timestamp - now) / 60),
            }
    return feed, sorted(arrivals.values(), key=lambda a: a["arrival_unix"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stops", nargs="+", required=True, help="Platform IDs for the station to inspect")
    parser.add_argument("--routes", nargs="+", default=["E", "F", "M", "R"])
    parser.add_argument("--feeds", nargs="+", choices=FEEDS, default=list(FEEDS))
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    result = {"stops": args.stops, "routes": args.routes, "feeds": [], "arrivals": [], "errors": []}
    for name in args.feeds:
        url = BASE + FEEDS[name]
        started = time.monotonic()
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "subway-led-matrix/phase4"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read(2_000_001)
            if len(data) > 2_000_000:
                raise ValueError("Feed exceeds 2 MB experiment limit")
            now = int(time.time())
            feed, arrivals = inspect(data, set(args.stops), set(args.routes), now)
            result["feeds"].append({"name": name, "url": url, "bytes": len(data),
                "entities": len(feed.entity), "timestamp": feed.header.timestamp,
                "age_seconds": now - feed.header.timestamp,
                "elapsed_seconds": round(time.monotonic() - started, 3)})
            result["arrivals"].extend(arrivals)
        except Exception as error:
            result["errors"].append({"feed": name, "error": str(error)})
    unique = {(a["route"], a["trip_id"], a["stop_id"]): a for a in result["arrivals"]}
    result["arrivals"] = sorted(unique.values(), key=lambda a: a["arrival_unix"])[:args.limit]
    print(json.dumps(result, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
