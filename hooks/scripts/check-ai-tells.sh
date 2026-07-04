#!/bin/bash
set -euo pipefail

input=$(cat)

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

case "$file_path" in
  *.md|*.markdown|*.txt) ;;
  *) exit 0 ;;
esac

content=$(cat -- "$file_path")

# High-confidence vocabulary and phrase tells (see ai-writing-guide.md).
tell_pattern='\b(delve|delves|delving|tapestry|multifaceted|nuanced|leverage|leveraging|utilize|utilizing|seamless|foster|fosters|pivotal|paramount|holistic|streamline|transformative|meticulous|intricate|embark|embarking|beacon|testament|plethora|myriad|moreover|furthermore|nevertheless|underscores|underscoring)\b'
phrase_pattern="it'?s not just [a-z ]+, it'?s|it is important to note that|in today'?s rapidly evolving|cannot be overstated|embark on a journey|a testament to"

word_hits=$(printf '%s' "$content" | { grep -Eio "$tell_pattern" || true; } | sort -u | tr '\n' ', ' | sed 's/, $//')
word_count=$(printf '%s' "$content" | { grep -Eio "$tell_pattern" || true; } | wc -l | tr -d ' ')
phrase_count=$(printf '%s' "$content" | { grep -Eio "$phrase_pattern" || true; } | wc -l | tr -d ' ')
em_dash_count=$(printf '%s' "$content" | { grep -o '—' || true; } | wc -l | tr -d ' ')
prose_words=$(printf '%s' "$content" | wc -w | tr -d ' ')

total_hits=$((word_count + phrase_count))

# Flag high em-dash density (roughly denser than 1 per 150 words) as an extra signal.
em_dash_flag=0
if [[ "$prose_words" -gt 0 && "$em_dash_count" -gt 0 ]]; then
  threshold=$((prose_words / 150))
  if [[ "$em_dash_count" -gt "$threshold" && "$em_dash_count" -ge 3 ]]; then
    em_dash_flag=1
  fi
fi

if [[ "$total_hits" -lt 2 && "$em_dash_flag" -eq 0 ]]; then
  exit 0
fi

message="nobots: $file_path was just written/edited and shows possible AI writing tells"
if [[ "$total_hits" -ge 2 ]]; then
  message="$message — vocabulary/phrase hits: $word_hits (${total_hits} total)."
fi
if [[ "$em_dash_flag" -eq 1 ]]; then
  message="$message Em dash density looks high ($em_dash_count in ~$prose_words words)."
fi
message="$message Consider a pass with the humanize-writing skill before finishing, or run detect-ai-writing for a full read. This is a non-blocking heuristic warning, not a verdict."

echo "$message" >&2
exit 2
