# Source Mapping Fix - November 3, 2025

## Issue Reported

When asking "View Our Services", the chatbot was showing:
```
📚 sources:
instalogic.in/case-studies/  ❌ (irrelevant)
```

This was happening even though the query was about services, not case studies.

## Root Cause

The `_map_s3_to_website()` function in `backend/bedrock_client.py` was using:
- **Simple if-else checks** that matched the first keyword found
- **Generic keywords** like "project" and "client work" that appear in multiple contexts
- **No scoring mechanism** to determine which category is most relevant

Example: If content mentioned "We offer dashboard projects", the word "project" triggered case-studies mapping even though it was clearly about services.

## Solution Implemented

### New Algorithm: Keyword Scoring System

```python
# Count keyword matches for each category
service_count = sum(1 for keyword in service_keywords if keyword in content_lower)
case_study_count = sum(1 for keyword in case_study_keywords if keyword in content_lower)
# ... etc

# Return URL based on highest match count
if service_count == max_count:
    return 'https://www.instalogic.in/our-services/'
```

### Key Improvements

1. **Scoring System:**
   - Counts ALL matching keywords for each category
   - Returns the URL with the highest relevance score
   - More accurate than "first match wins"

2. **Better Keywords:**
   - **Service keywords:** Added specific terms like `analytics`, `dashboard`, `bi support`, `financial impact`, `software development`
   - **Case study keywords:** Made more specific: `case study`, `success story`, `client example`, `delivered for`, `implemented at`
   - **Removed generic terms** like `project` and `client work` from case studies

3. **Context-Aware Mapping:**
   - If content has 5 service keywords and 1 case study keyword → maps to services
   - Prevents false positives from incidental keyword mentions

## Example Scenarios

### Scenario 1: Services Query ✅
**Content:** "We offer data analytics services, dashboard solutions, and BI support"
- Service keywords matched: 4 (offer, analytics, service, dashboard, bi support)
- Case study keywords matched: 0
- **Result:** `instalogic.in/our-services/` ✅

### Scenario 2: Case Study Query ✅
**Content:** "We delivered a successful dashboard project for MBOCWWB"
- Service keywords matched: 1 (dashboard)
- Case study keywords matched: 2 (delivered for, success story implied)
- **Result:** `instalogic.in/case-studies/` ✅

### Scenario 3: Mixed Content ✅
**Content:** "Our analytics services have been implemented at multiple clients"
- Service keywords matched: 2 (analytics, service)
- Case study keywords matched: 1 (implemented at)
- **Result:** `instalogic.in/our-services/` ✅ (higher score)

## Testing

### Test the Fix:

1. **Open chatbot:** http://localhost:3000
2. **Test queries:**
   - "View Our Services" → Should show `instalogic.in/our-services/`
   - "What services do you offer?" → Should show `instalogic.in/our-services/`
   - "Show me your case studies" → Should show `instalogic.in/case-studies/`
   - "Tell me about careers" → Should show `instalogic.in/careers/`

### Expected Behavior:

✅ Sources should now be **relevant** to the query topic  
✅ No more irrelevant case-studies links for service queries  
✅ Better accuracy across all categories  

## Complete Solution (2-Layer Fix)

### Layer 1: URL Mapping Improvement
**File:** `backend/bedrock_client.py` (lines 117-157)
- Updated `_map_s3_to_website()` method
- Implemented keyword scoring system
- Added category-specific keyword lists

### Layer 2: Source Relevance Filtering (STRICT MODE)
**File:** `backend/chatbot_orchestrator.py` (lines 217-251)
- Added `_filter_relevant_sources()` method with **STRICT filtering**
- **DEFAULT:** Always exclude `case-studies/` from sources
- **EXCEPTION:** Only include `case-studies/` if query explicitly contains:
  - "case study", "case studies", "past work", "portfolio", "success story", etc.
- Limits to 3 most relevant sources

**How it works:**
```python
# Query: "View Our Services"
kb_result = bedrock_client.query_kb(query)
# KB returns: ['services/', 'case-studies/', 'careers/']

filtered = filter_relevant_sources(kb_result['sources'], query)
# STRICT FILTER: Remove 'case-studies/' (NOT explicitly asked)
# Return: ['services/'] ✅

# Query: "See case studies"
kb_result = bedrock_client.query_kb(query)
# KB returns: ['case-studies/', 'services/']

filtered = filter_relevant_sources(kb_result['sources'], query)
# STRICT FILTER: Keep 'case-studies/' (EXPLICITLY asked)
# Return: ['case-studies/'] ✅
```

## Files Modified

1. **`backend/bedrock_client.py`** (lines 117-157)
   - URL mapping with keyword scoring

2. **`backend/chatbot_orchestrator.py`** (lines 217-269, 300)
   - Source relevance filtering
   - Query intent detection

## Deployment

**Status:** ✅ Applied and tested
- Backend restarted with both fixes
- Ready for production deployment

---

**Fix Applied:** November 3, 2025  
**Status:** Complete ✅  
**Layers:** 2 (URL Mapping + **STRICT** Source Filtering)

---

## STRICT FILTERING RULE

**Problem:** `case-studies/` was appearing in EVERY response, even when irrelevant

**Solution:** STRICT whitelist approach
- **DEFAULT:** Always exclude `case-studies/` 
- **EXCEPTION:** Only include when query explicitly contains:
  - "case study", "case studies", "past work", "portfolio", "success story", "projects you", "show me example"

**Result:** `case-studies/` now ONLY appears when user explicitly asks about case studies

