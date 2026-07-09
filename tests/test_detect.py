from nobots.core.detect import detect_text, QUORUM


AI_SAMPLE = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation. This is a testament to progress. It underscores the "
    "importance of synergy. Furthermore, we leverage seamless solutions — every day "
    "— to foster growth — across teams — and streamline outcomes — at scale — for "
    "all. Moreover, this pivotal moment cannot be overstated. It is important to "
    "note that we embark on a journey. We utilize holistic frameworks. We showcase "
    "meticulous care. We emphasize intricate detail. Nevertheless, the paramount "
    "goal remains. It plays a crucial role. This marks a pivotal moment for us all."
)

HUMAN_SAMPLE = (
    "I broke the build again yesterday. Classic. The fix took four minutes; finding "
    "it took two hours because the error message pointed at the wrong file. Anyway, "
    "here's what actually happened. Our deploy script assumes the config lives in "
    "/etc/app, but staging puts it in /opt. Nobody wrote that down. So when I copied "
    "the prod playbook to staging, everything looked fine until the healthcheck fell "
    "over at 3am. Lesson: check where the config lives before you trust the playbook. "
    "I added a one-line assert. Should've done that months ago."
)


def test_ai_sample_crosses_quorum():
    result = detect_text(AI_SAMPLE)
    assert result.tells_found is True
    assert result.agree >= QUORUM


def test_human_sample_below_quorum():
    result = detect_text(HUMAN_SAMPLE)
    assert result.tells_found is False


def test_single_family_abstains():
    # One vocabulary hit, ordinary punctuation/rhythm — one family at most.
    text = "We should leverage this tool. " + "It works well for the team. " * 20
    result = detect_text(text)
    assert result.agree < QUORUM
    assert result.tells_found is False
