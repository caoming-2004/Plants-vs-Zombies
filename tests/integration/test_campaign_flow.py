from pvz_game.config import load_campaign
from pvz_game.domain import campaign as rules
from pvz_game.progress import Progress


def test_campaign_unlock_chain_and_retry_state(progress_path):
    config, campaign, levels = load_campaign()
    progress = Progress.load(progress_path)
    assert progress.is_unlocked("day_01")
    assert not progress.is_unlocked("day_02")

    progress.record_win("day_01", campaign["stages"], stars=1, ticks=10000)
    progress.save()
    assert progress.is_unlocked("day_02")
    assert rules.next_stage(campaign, "day_01") == "day_02"

    # A failed run is represented by not recording a win; retry state is a fresh Progress.
    retry = Progress.load(progress_path)
    assert retry.is_unlocked("day_02")
    assert not retry.is_unlocked("day_03")

    for level_id in campaign["stages"][1:]:
        retry.record_win(level_id, campaign["stages"], stars=0, ticks=10000)
    assert retry.endless_unlocked