# TODO - Planned Improvements

This document outlines planned improvements for the Waldo application, prioritized by impact and effort.

## 🎯 **Priority Ranking & Time Estimates**

### **🚀 HIGH IMPACT, LOW EFFORT (Do First)**

**1. Real-time Processing Updates** ⭐ **TOP PRIORITY**
- **Impact**: Massive UX improvement, eliminates "black box" feeling
- **Effort**: Low-Medium  
- **Time**: 2-3 hours
- **Implementation**: WebSocket or Server-Sent Events for live status updates

**2. Different Markers for Location Types** ⭐ 
- **Impact**: High visual value, better information architecture
- **Effort**: Low
- **Time**: 1-2 hours  
- **Implementation**: Extend `createCustomMarker()` with type-based styling

### **⚡ HIGH IMPACT, MEDIUM EFFORT (Do Second)**

**3. Improve Processing Time** 
- **Impact**: High (better user experience)
- **Effort**: Medium
- **Time**: 3-4 hours
- **Implementation**: Async processing, parallel geocoding, caching

**4. Handle Longer Articles**
- **Impact**: Medium-High (enables more use cases)
- **Effort**: Medium  
- **Time**: 2-3 hours
- **Implementation**: Chunking strategy, sliding window processing

### **🧪 MEDIUM IMPACT, HIGH EFFORT (Do Later)**

**5. TDD for Prompts**
- **Impact**: Medium (quality/reliability improvement)
- **Effort**: High
- **Time**: 4-6 hours
- **Implementation**: Prompt testing framework, golden datasets

## 📋 **Additional Improvements**

### **🎯 High Priority Additions**

**6. Caching Layer** ⭐ **CRITICAL**
- **Why**: Geocoding is expensive, articles repeat
- **Time**: 1-2 hours
- **Implementation**: Redis or in-memory cache for geocoding results

**7. Error Recovery & Retry Logic** ⭐
- **Why**: Network failures, API timeouts happen
- **Time**: 1-2 hours  
- **Implementation**: Exponential backoff, partial results handling

**8. Performance Monitoring**
- **Why**: Track processing bottlenecks
- **Time**: 1 hour
- **Implementation**: Timing metrics, slow query detection

### **🔧 Medium Priority Additions**

**9. Batch Processing for Multiple Articles**
- **Why**: Power user feature, better resource utilization
- **Time**: 3-4 hours

**10. Location Confidence Visualization**
- **Why**: Show uncertainty in AI predictions
- **Time**: 1-2 hours

**11. Article Content Preview**
- **Why**: User validation before processing
- **Time**: 1 hour

## 📊 **Recommended Implementation Order**

### **Phase 1: Quick Wins (6-8 hours)**
1. ✅ Real-time processing updates (3h)
2. ✅ Different location type markers (1h) 
3. ✅ Caching layer (2h)
4. ✅ Error recovery (2h)

### **Phase 2: Performance & Scale (8-10 hours)**
5. ✅ Processing time improvements (4h)
6. ✅ Longer article handling (3h)
7. ✅ Performance monitoring (1h)
8. ✅ Location confidence visualization (2h)

### **Phase 3: Advanced Features (6-8 hours)**
9. ✅ TDD for prompts (5h)
10. ✅ Batch processing (3h)

## 🎯 **Current Focus**

**Priority 1: Real-time Processing Updates**

Implementation plan:
1. WebSocket connection for live updates
2. Progress tracking in the backend 
3. Status UI components in the frontend
4. Structured progress messages ("Extracting article...", "Finding 8 locations...", "Geocoding Paris, France...")

## 📝 **Implementation Notes**

### Real-time Updates Implementation Details
- Use Server-Sent Events (simpler than WebSocket for one-way communication)
- Progress states: `extracting` → `locations_found` → `geocoding` → `summarizing` → `complete`
- Include counts and current item being processed
- Graceful degradation if SSE not supported

### Location Type Markers
- Current location types: city, state, country, landmark, region, nickname, generic
- Color coding: countries (red), states (blue), cities (green), landmarks (purple), etc.
- Icon variations: different shapes or symbols per type

### Caching Strategy
- Geocoding cache: location_name → coordinates (TTL: 7 days)
- Article content cache: url → extracted_text (TTL: 1 day)
- LLM response cache: text_hash → locations (TTL: 1 hour)