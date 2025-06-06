import json
import os
import re
import sys

THRESHOLD = 0.3
TIME_RE = re.compile(r"\((\d{1,3}:\d{2})\s*,\s*(\d{1,3}:\d{2})\)")
ACTIONS = [
    "corner",
    "shots on target",
    "goal",
    "clearance",
    "foul",
    "free-kick",
    "substitution"
]

def get_time_in_sec(time: str) -> int:
    time_parts = time.split(":")
    return int(time_parts[0]) * 60 + int(time_parts[1])

def parse_timestamps(out: str) -> list[tuple[int, int]]:
    time_list = []
    time_pairs = TIME_RE.findall(out)
    for pair in time_pairs:
        start, end = pair
        start_time = get_time_in_sec(start)
        end_time = get_time_in_sec(end)
        time_list.append((start_time,  end_time))
    return time_list

def iou(interval1: tuple[int, int], interval2: tuple[int, int]) -> float:
    start1, end1 = interval1
    start2, end2 = interval2
    inter_start = max(start1, start2)
    inter_end = min(end1, end2)
    intersection = max(0, inter_end - inter_start)
    union = max(end1, end2) - min(start1, start2)
    return intersection / union if union > 0 else 0

def compare_outputs(pred: list[tuple[int, int]], gt: list[tuple[int, int]]) -> tuple[int, int]:
    matched = 0
    matched_preds = set()
    for gt_range in gt:
        best_iou = 0
        for idx, pred_range in enumerate(pred):
            score = iou(gt_range, pred_range)
            if score >= THRESHOLD:      # Found some GT matching the prediction
                matched_preds.add(idx)
            if score > best_iou:
                best_iou = score
        if best_iou >= THRESHOLD:       # GT has some matching prediction
            matched += 1
    return len(matched_preds), matched


def parse_action(out: str) -> str:
    for action in ACTIONS:
        if re.search(action, out, re.IGNORECASE):
            return action

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise "Expected JSON filename as input"
    filenames = sys.argv[1:]
    all_metrics = {}
    for filename in filenames:
        with open(filename, "r") as f:
            results = json.load(f)

        gt_counts = {}
        pred_counts = {}
        match_counts_pred = {}
        match_counts_gt = {}

        for result in results:
            predictions = result.get("prediction", result.get("result"))
            if isinstance(predictions, list):
                predictions = predictions[0]
            pred = parse_timestamps(predictions)
            gt = parse_timestamps(result["ground_truth"])
            action = parse_action(result["ground_truth"])
            pred_matches, gt_matches = compare_outputs(pred, gt)
            match_counts_pred[action] = match_counts_pred.get(action, 0) + pred_matches
            match_counts_gt[action] = match_counts_gt.get(action, 0) + gt_matches
            gt_counts[action] = gt_counts.get(action, 0) + len(gt)
            pred_counts[action] = pred_counts.get(action, 0) + len(pred_counts)

        precision_map = {}
        recall_map = {}
        f1_map = {}
        for action in ACTIONS:
            precision = match_counts_pred.get(action, 0) / pred_counts.get(action, 1)
            recall = match_counts_gt.get(action, 0) / gt_counts.get(action, 1)
            precision_map[action] = precision
            recall_map[action] = recall
            f1_map[action] = 2 * recall * precision / (recall + precision) if recall + precision else 0

        total_precision = sum(match_counts_pred.values()) / sum(pred_counts.values()) if sum(pred_counts.values()) else 0
        total_recall = sum(match_counts_gt.values()) / sum(gt_counts.values()) if sum(gt_counts.values()) else 0
        total_f1 = 2 * total_recall * total_precision / (total_recall + total_precision) if total_recall + total_precision else 0

        metrics = {}
        metrics["precision"] = total_precision
        metrics["recall"] = total_recall
        metrics["f1"] = total_f1
        metrics["action-wise precision"] = precision_map
        metrics["action-wise recall"] = recall_map
        metrics["action-wise f1"] = f1_map
        all_metrics[os.path.splitext(os.path.basename(filename))[0]] = metrics
    print()
    print(json.dumps(all_metrics, indent=4))
