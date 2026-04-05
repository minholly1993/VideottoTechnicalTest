"""
Speaker ID debouncing for stable camera tracking.

Removes rapid speaker-ID bounces that cause jarring crop window snaps.
"""


def debounce_speaker_ids(speaker_track_ids, min_hold_frames=15):
    """
    Remove rapid speaker-ID bounces shorter than min_hold_frames.

    Speaker detection sometimes flickers the active-speaker label during
    crosstalk or brief classification uncertainty, producing 1-10 frame
    segments that cause jarring rapid-fire crop snaps. This pre-filter
    replaces those short segments with the surrounding stable speaker ID
    so the downstream dead-zone tracker never sees them.

    Algorithm:
      1. Run-length encode the raw IDs into (track_id, start, length) runs.
      2. For any run shorter than min_hold_frames, replace it with the
         previous stable run's ID (or the next stable run if it's the first).
      3. Expand back to a per-frame list.

    Args:
        speaker_track_ids: Per-frame list of speaker IDs (int or None).
            None means no speaker detected at that frame.
        min_hold_frames: Minimum frames a speaker must hold to be "stable".

    Returns:
        Same-length list with short flicker runs replaced by nearest stable ID.
        None segments are never modified.

    Examples:
        >>> debounce_speaker_ids([0]*50 + [1]*3 + [0]*50, min_hold_frames=10)
        [0]*103  # The 3-frame speaker-1 segment is replaced by speaker 0

        >>> debounce_speaker_ids([None]*10 + [0]*50, min_hold_frames=15)
        [None]*10 + [0]*50  # None segments are untouched
    """
    if not speaker_track_ids:
        return []

    tracks = []
    cur = 0
    for i in range(1, len(speaker_track_ids)):
        if speaker_track_ids[i] != speaker_track_ids[cur]:
            tracks.append([speaker_track_ids[cur], cur, i - cur])
            cur = i
    tracks.append([speaker_track_ids[cur], cur, len(speaker_track_ids) - cur])

    for i in range(len(tracks)):
        track_id, start, length = tracks[i]
        if track_id is not None:
            if length < min_hold_frames:
                replace = None
                if i == 0:
                    replace_id, replace_start, replace_len = tracks[i+1]
                elif i > 0:
                    replace_id, replace_start, replace_len = tracks[i-1]
                if replace_id is not None and replace_len >= min_hold_frames:
                    replace = replace_id
                if replace is not None:
                    tracks[i] = (replace, start, length)
                else:
                    tracks[i] = tuple(tracks[i])

    output = [None] * len(speaker_track_ids)
    for track_id, start, length in tracks:
        if track_id is not None:
            for i in range(start, start+length):
                output[i] = track_id

    return output
    # raise NotImplementedError("TODO: Implement this function — see docstring for spec")

def testcases():
    # error case
    data = [0]*50 + [1]*3 + [0]*50
    out = debounce_speaker_ids(data)
    assert all(x == 0 for x in out)

    # normal case
    data = [0]*50 + [1]*20 + [0]*50
    out = debounce_speaker_ids(data)
    assert out[50:70] == [1]*20

    # None case
    data = [None]*10 + [0]*50
    out = debounce_speaker_ids(data)
    assert out[:10] == [None]*10

    # edge case
    data = [0]*15 + [1]*15 + [0]*15
    out = debounce_speaker_ids(data)
    assert out[15:30] == [1]*15
