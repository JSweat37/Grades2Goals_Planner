# Regex & String Parsing Cheat Sheet  

This cheat sheet summarizes the common regex and string symbols we used in Notebook 05 for parsing study plans.  

---

## Regex Basics  
| Symbol | Meaning | Example | Matches |  
|--------|---------|---------|----------|  
| `^` | Start of line | `^Day` | "Day 1 tasks" / not "Some Day" |  
| `$` | End of line | `end$` | "weekend" / not "endless" |  
| `.` | Any single character | `a.c` | "abc", "axc" |  
| `*` | Zero or more of previous | `lo*l` | "ll", "lol", "loool" |  
| `+` | One or more of previous | `\d+` | "123", "7" |  
| `?` | Optional (0 or 1) | `colou?r` | "color", "colour" |  
| `\s` | Whitespace | `a\sb` | "a b" |  
| `\d` | Digit (0–9) | `\d+` | "25", "2024" |  
| `\b` | Word boundary | `\bcat\b` | "cat" / not "concatenate" |  
| `|` | OR | `dog|cat` | "dog", "cat" |  

---

## Groups & Captures  
| Symbol | Meaning | Example | Matches |  
|--------|---------|---------|----------|  
| `(…)` | Capturing group | `(Day\s*\d+)` | "Day 3" → group = "Day 3" |  
| `(?:…)` | Non-capturing group | `(?:abc)+` | Matches "abcabc", but not saved |  
| `(…)|(…)` | Alternatives | `(dog|cat)` | "dog", "cat" |  

---

## In Our Code  

### Day header detection  
```python
m_day = re.match(r"^(?:#+\s*)?Day\s*(\d+)", line, flags=re.IGNORECASE)

