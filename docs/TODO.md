# TODO - Planned Improvements

This document outlines planned improvements for the Waldo application, prioritized by impact and effort.

## 🎯 **Priority Ranking & Time Estimates**

### **🚀 HIGH IMPACT, LOW EFFORT (Do First)**

**1. ✅ Real-time Processing Updates** ⭐ **COMPLETED**
- **Impact**: Massive UX improvement, eliminates "black box" feeling
- **Effort**: Low-Medium  
- **Time**: 2-3 hours
- **Implementation**: ✅ Server-Sent Events implemented with progress_tracker.py and realtime.js

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
1. ✅ Real-time processing updates (3h) - **COMPLETED**
2. ⭐ Different location type markers (1h) - **NEXT PRIORITY**
3. ⭐ Caching layer (2h) - **HIGH PRIORITY**
4. ⭐ Error recovery (2h) - **HIGH PRIORITY**

### **Phase 2: Performance & Scale (8-10 hours)**
5. ⭐ Processing time improvements (4h) - **TODO**
6. ⭐ Longer article handling (3h) - **TODO**
7. ⭐ Performance monitoring (1h) - **TODO**
8. ⭐ Location confidence visualization (2h) - **TODO**

### **Phase 3: Advanced Features (6-8 hours)**
9. ⭐ TDD for prompts (5h) - **TODO**
10. ⭐ Batch processing (3h) - **TODO**

## 🎯 **Current Focus**

**✅ COMPLETED: Real-time Processing Updates**

✅ **Implementation completed:**
1. ✅ Server-Sent Events connection for live updates
2. ✅ Progress tracking in the backend with progress_tracker.py
3. ✅ Status UI components in the frontend with realtime.js
4. ✅ Structured progress messages ("Extracting article...", "Finding 8 locations...", "Geocoding Paris, France...")

**🎯 NEXT PRIORITY: Different Markers for Location Types**

Implementation plan:
1. Extend `createCustomMarker()` with location type parameter
2. Create different colors/shapes for: city, state, country, landmark, region
3. Update `addMarkers()` to use location type from data
4. Add legend showing marker types

## 📝 **Implementation Notes**

### ✅ Real-time Updates Implementation Details - COMPLETED
- ✅ Server-Sent Events implemented (progress_tracker.py + realtime.js)
- ✅ Progress states: `starting` → `extracting_article` → `extracting_locations` → `processing_locations` → `filtering` → `complete`
- ✅ Include counts and current item being processed
- ✅ Graceful degradation if SSE not supported

### Location Type Markers
- Current location types: city, state, country, landmark, region, nickname, generic
- Color coding: countries (red), states (blue), cities (green), landmarks (purple), etc.
- Icon variations: different shapes or symbols per type

### Caching Strategy
- Geocoding cache: location_name → coordinates (TTL: 7 days)
- Article content cache: url → extracted_text (TTL: 1 day)
- LLM response cache: text_hash → locations (TTL: 1 hour)