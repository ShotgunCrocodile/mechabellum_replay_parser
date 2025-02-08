import argparse
import os
import statistics
import unicodedata

from dataclasses import dataclass, field
from typing import List, Dict

from src.mechabellum_replay_parser import parse_battle_record


def get_display_width(text: str) -> int:
    """Calculate display width of text considering full-width characters."""
    return sum(2 if unicodedata.east_asian_width(char) in 'WF' else 1 for char in text)


def pad_text(text: str, width: int) -> str:
    """Pad text to align properly by considering full-width characters."""
    pad_size = width - get_display_width(text)
    return text + " " * pad_size


@dataclass
class Report:
    successful: List[str] = field(default_factory=list)
    failed: Dict[str, str] = field(default_factory=dict)
    player_statistics: List[Dict[str, float]] = field(default_factory=list)

    def add_success(self, file_path: str):
        self.successful.append(file_path)

    def add_failure(self, file_path: str, error: str):
        self.failed[file_path] = error

    def add_player_stat(self, replay_name: str, player_name: str, mean_y_distance: float):
        self.player_statistics.append({
            "replay": replay_name,
            "player": player_name,
            "mean_y_distance": mean_y_distance
        })

    def display(self):
        print("\nProcessing Report:")
        print(f"Successful: {len(self.successful)}")
        for file in self.successful:
            print(f"  - {file}")
        print(f"Failed: {len(self.failed)}")
        for file, error in self.failed.items():
            print(f"  - {file}: {error}")

        if not self.player_statistics:
            print("No valid data available.")
            return

        # Determine column widths based on longest values
        replay_col_width = max(
            get_display_width(stat['replay']) for stat in self.player_statistics + [{'replay': 'Replay Name'}])
        player_col_width = max(
            get_display_width(stat['player']) for stat in self.player_statistics + [{'player': 'Player Name'}])
        distance_col_width = len("Mean Y Distance")

        # Header
        header = f"{pad_text('Replay Name', replay_col_width)} | {pad_text('Player Name', player_col_width)} | {pad_text('Mean Y Distance', distance_col_width)}"
        separator = "-" * len(header)
        print("\n" + header)
        print(separator)

        mean_y_values = []
        for stat in self.player_statistics:
            print(
                f"{pad_text(stat['replay'], replay_col_width)} | {pad_text(stat['player'], player_col_width)} | {pad_text(str(round(stat['mean_y_distance'], 2)), distance_col_width)}")
            mean_y_values.append(stat['mean_y_distance'])

        print(separator)
        overall_mean = statistics.mean(mean_y_values)
        print(
            f"{pad_text('Overall Mean Y Distance', replay_col_width + player_col_width + 3)} | {pad_text(str(round(overall_mean, 2)), distance_col_width)}")


def process_replay_files(directory: str):
    report = Report()

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if not file_name.endswith('.grbr'):
            continue
        try:
            battle_record = parse_battle_record(file_path)
            report.add_success(file_path)

            for player in battle_record.player_records:
                if player.deployments and player.deployments.units:
                    last_round_units = player.deployments.units[-1]

                    y_positions = [
                        abs(unit.position.y)
                        for unit in last_round_units.units.values() if unit.position
                    ]

                    if y_positions:
                        mean_y_distance = statistics.mean(y_positions)
                        report.add_player_stat(file_name, player.name, mean_y_distance)

        except Exception as e:
            report.add_failure(file_path, str(e))

    report.display()


def main():
    parser = argparse.ArgumentParser(description="Process replay files in bulk.")
    parser.add_argument("directory", help="Directory containing replay files.")
    args = parser.parse_args()

    process_replay_files(args.directory)


if __name__ == "__main__":
    main()
