# Slide Development Guide

> This document explains how to develop custom slide components in **MGX Presentation**.

## Basic Conventions

| Project | Requirements |
|---|---|
| **Menu** | All slides are placed in the `src/pages/slides/` directory, one file corresponds to one Slide |
| **Naming** | The file name is the component name, ensure `id` is globally unique |
| **Export** | Must `export default` the component itself |
| **Registration** | Use `RegisterSlide({ ... })(Component)` to complete registration |
| **Size** | Fixed **1280 × 720 (16:9)** canvas design |

## File Structure
- `index.html` - HTML entry point
- `vite.config.ts` - Vite configuration file
- `tailwind.config.js` - Tailwind CSS configuration file
- `package.json` - Project dependencies and scripts
- `src/app.tsx` - Root component, sets up global Providers (e.g., QueryClientProvider, Router), UI config, and routes
- `src/main.tsx` - Project entry point
- `src/index.css` - Existing CSS configuration
- `src/pages/Index.tsx` - Home page logic
- `src/components/ui/` - Reusable UI components
- `src/components/core/` - Core components (e.g., PPTContainer.tsx, PPTNavigation.tsx, SlideRegistry.ts) for slide rendering and management
- `src/decorators/RegisterSlide.ts` - Slide registration decorator
- `src/hooks/useSlideAnimation.ts` - Element animation hook
- `src/types/ppt.ts` - PPT types

## Element Animation (Optional)

```tsx
import { useSlideAnimation } from "@/hooks/useSlideAnimation";

const Demo: React.FC = () => {
  const titleRef = useRef<HTMLHeadingElement>(null);
  const api = useSlideAnimation();

  useEffect(() => {
    api
      .addElement("title", titleRef, {
        enter: { type: "slideInLeft", duration: 600 },
        group: 0,
      })
      .setMode("parallel")
      .startGrouped();
  }, []);

  return <h1 ref={titleRef}>Title</h1>;
};
```
**Note**：Element animation is only enabled in full screen preview.

**Warning**: Never use variable names that conflict with React hooks (e.g., naming a variable `useRef`, `useState`, etc.) as it will cause initialization errors.

## Image Processing Best Practices

1. **Generate AI Images**: Always use ImageCreator.generate_image to create high-quality, contextually relevant images. This provides stable, consistent results tailored to your content needs.

**ImageCreator Command Format:**
```xml
<ImageCreator.generate_image>
<description>Detailed visual description including subject, mood, elements, colors, and composition</description>
<filename>descriptive-image-name.jpg</filename>
<style>photorealistic|cartoon|sketch|watercolor|minimalist|3d</style>
</ImageCreator.generate_image>
```

**Parameter Guidelines:**
- `<description>`: Be specific and detailed about the visual content. Include subject, elements, atmosphere, colors, and composition - do NOT include style keywords (e.g., "Modern office workspace with large windows, natural lighting, minimalist furniture, plants, warm atmosphere with soft shadows")
- `<filename>`: Use descriptive kebab-case names with .jpg extension (e.g., "modern-office-workspace.jpg")
- `<style>`: Choose from available styles:
  - `photorealistic` - Photorealistic, high detail, professional photography
  - `cartoon` - Cartoon style, colorful, animated
  - `sketch` - Pencil sketch, black and white, artistic
  - `watercolor` - Watercolor painting, soft edges, artistic
  - `minimalist` - Minimalist design, clean, simple
  - `3d` - 3D render, blender, octane render

2. **Image Layout with Dynamic Height Control** (PREVENTS OVERFLOW):
   **Use Flex Layout for Auto-Adaptive Images:**
   ```tsx
   // ✅ BEST: Flex layout - images adapt to remaining space automatically
   <section className="flex h-full flex-col px-16 py-12">
     {/* Fixed height: title */}
     <h1 className="text-5xl font-bold mb-6">Title</h1>
     
     {/* Flexible: auto fills remaining space */}
     <div className="flex-1 min-h-0 grid grid-cols-2 gap-8">
       <div className="space-y-4">
         {/* Text content */}
       </div>
       
       {/* Image container: automatically sized */}
       <div className="flex flex-col gap-4 min-h-0">
         <div className="flex-1 min-h-0">
           <img src="/assets/image1.jpg" alt="Desc" 
                className="w-full h-full object-cover rounded-lg" />
         </div>
         <div className="flex-1 min-h-0">
           <img src="/assets/image2.jpg" alt="Desc" 
                className="w-full h-full object-cover rounded-lg" />
         </div>
       </div>
     </div>
   </section>
   ```
   
   **Key Classes Explained:**
   - `flex-1`: Element grows to fill remaining space
   - `min-h-0`: Fixes flex container overflow issue (REQUIRED!)
   - `h-full`: Image fills its container height
   - `object-cover`: Crops image to fit (alternative: `object-contain` shows full image)

## Specification

- **Chart Components**：Use `Chart` component in `src/components/ui/chart.tsx`. The Chart component uses Recharts API and **REQUIRES** these properties:
  - `type`: Required - one of "line", "bar", "area", "pie", or "radar"
  - `data`: Required - array of data objects
  - `series`: Required - array of data key strings to plot
  - `xKey`: Optional - category field name (default: "x")
  - `colors`: Optional - array of color strings
  - `height`: Optional - chart height in pixels (default: 260)

- **Core Files**：Do not modify files under `src/components/core/`

# Design Guidelines

## Design Style Guide
All slides MUST maintain consistent background colors throughout the presentation. Use variations of the SAME color family (e.g., from-blue-50 to-blue-100) - DO NOT mix drastically different backgrounds (blue → red → green). Visual coherence is mandatory.
Images and charts are PRIMARY content, text is SECONDARY. Images should be large and prominent, not small decorations. Balance text density with strong visual elements.
Use charts and images whenever possible. Emphasize the clarity of charts (bar charts, pie charts, line charts) using a variety of shapes and strong contrast. Use the ImageCreator tool to generate contextually relevant, high-quality images that match your presentation theme.
The combined bounds of slide elements (text blocks, charts, images) must fit within the **1280 × 720 (16:9)** resolution and must not extend beyond the slide boundaries.


**Automatic Overflow Detection (Enhanced with AI):**
The system includes intelligent overflow detection with simplified mode (default):
- **Simple Mode (Default)**: Focuses on 3 core checks - height analysis with card block statistics, body overflow, and vertical overflow
- **Height Analysis**: Automatically counts and analyzes all card/content blocks on the page
- **Smart Recommendations**: Suggests exact number of cards to remove based on overflow amount
- **Card Block Detection**: Identifies elements with class names like 'card', 'box', 'panel', or visual features (background + border/shadow/padding)
- Detection runs in background and provides actionable fix suggestions in console

**Example Detection Output:**
```
🎴 Card/Block Analysis:
  Total card blocks found: 4
  Average card height: 170px
  
  💡 Recommendation: Content overflows by 130px
     → Consider removing 1 card block(s) to fix overflow
     → Current: 4 cards, suggest: 3 cards
```

**Mandatory Rules:**
1. **Always use `h-full` on the root `<section>` tag**: This ensures the section fills the container exactly

2. **[CRITICAL] Vertical Stacking Rule - STRICTLY ENFORCED**:
   - **DETECTION**: If your slide has 4+ content blocks (cards, features, points), you MUST use grid layout
   - **REQUIRED ✅**: 
     * For 1-3 items: Use vertical layout `flex flex-col space-y-4` or `space-y-6`
     * For 4+ items: MUST use horizontal grid `grid grid-cols-2 gap-4` or `grid-cols-3 gap-4`
     * Alternative: Split content into 2 separate slides (recommended for 6+ items)
   - **Card/Box Definition**: Any `<div>` with background, border, padding, or shadow (feature cards, info boxes, stat cards, process steps, etc.)

3. **Control spacing carefully**:
   - Use `gap-4` to `gap-8` (16px-32px) between elements, avoid `gap-12` or larger
   - Use `space-y-4` to `space-y-6` for vertical spacing


## Slide Structure Guidelines

### 1. Cover Slide

**Typography**:
- Main Title: `text-6xl font-bold` (60px) - use **Main Title** from Typography System
- Subtitle: `text-3xl` (30px) - use **Section Title** sizing
- Metadata: `text-xl` or `text-lg` (20px/18px)

**Visual Elements**:
- **Use HERO Images as backgrounds**: Used a HERO Image as background. Large, impactful background images are essential for professional presentations. Hero images should cover the full slide area and create visual depth.

**Layout Requirements**:
- Center-align all text for visual balance
- Ensure ample whitespace - title should be the clear focal point
- Use Image as the bottom background of the entire cover page.

---
### 2. Table of Contents Slide
**Design Principles**:
- Use consistent numbering or icons for each section
- Apply `gap-8` spacing between items (following 8px grid system)
- Limit to 4-6 sections maximum (if more, consider splitting or grouping)
- ONE accent color only (primary theme color)
---

### 3. Content Slides Content slides vary by purpose. Choose the appropriate pattern from the Layout Pattern Library: 

#### 3.1 Data/Statistics Slide **Requirements**: - **Title**: Outcome-oriented, not descriptive - **Chart**: Prominent, taking 50-60% of slide space - **Labels**: text-base for data labels 

#### 3.2 Process/Timeline Slide **Design Notes**: - Limit to 3-5 steps maximum - Use consistent node styling (circles with accent color) - Text below each node: title in text-xl font-semibold, description in text-base 

#### 3.3 Feature/Benefit Slide **Requirements**: - Cards with shadow-lg, rounded-2xl - Icon area: w-24 h-24, background in light theme color - Text hierarchy: title text-2xl font-semibold, description text-lg 

#### 3.4 Image-Focused Slide

**Image Guidelines**:
- **ALWAYS generate images using ImageCreator** - no placeholders
- Styling: Keep images clean and simple (no rounded corners or shadows by default)
- Images should be PRIMARY content, not decoration

---

### 4. Closing/Thank You Slide

**Design Principles**:
- Echo the cover slide's color scheme for cohesion
- Keep it minimal - "Thank You" should be the focal point
- Center-align all content
- Optional elements: summary quote, contact info, QR code, logo
- Use same background gradient as cover slide

## Slide Content Creation Process

### Workflow Overview
The slide creation process consists of two distinct phases:
1. **Phase A: Global Preparation** (once for entire presentation)
2. **Phase B: Per-Slide Creation Loop** (repeated for each slide)

---

## Phase A: Global Preparation

Complete ALL steps in this phase BEFORE creating any individual slides. This ensures all resources (outlines, search results, images) are ready for efficient slide construction.

### A1. Generate Presentation Outline
Create a todo.md file with structured entries for each slide:

```markdown
#### Slide 1: [Slide Title]
slide_type: Cover
key_points:
- Main title and theme
- Subtitle or tagline
- Visual style direction

#### Slide 2: [Slide Title]
slide_type: Content | Data | Analysis
key_points:
- Key point 1
- Key point 2
- Key point 3
```

### A2. Validate & Prevent Overflow
For EACH content slide in your outline, count content blocks (cards, feature boxes, stat boxes, process steps):

**Critical Rule**: 4+ content blocks WILL cause overflow in 720px height
- **1-3 blocks**: Use vertical layout `flex flex-col space-y-4`
- **4+ blocks**: MUST use `grid grid-cols-2 gap-4` OR split into 2 slides
- **Flag** any slide with 4+ blocks and adjust outline accordingly

### A3. Batch Information Retrieval (CRITICAL for Content Richness)

**Query Strategy - Be Specific and Request Details:**

```markdown
❌ BAD: "What is AI?" (too vague)
✅ GOOD: "What is AI? Include definition, history, 3-4 real-world examples with company names, and key statistics"

❌ BAD: "Machine learning types"  
✅ GOOD: "Explain supervised, unsupervised, and reinforcement learning with concrete examples and applications"
```

**Search Volume per Slide:**
- **1-2 searches per content slide** (Cover/End slides: 0-1 searches)
- Each search should yield **200-300 words minimum**
- Always request: examples, statistics, company names, dates, case studies

**Storage Format in todo.md:**

```markdown
#### Slide 2: Machine Learning Types
slide_type: Content

### Search Results Cached:
**Query 1: "What is machine learning? Include definition, core principles, 3 real-world examples"**
Result: [200-300 words with specific examples like "Netflix uses ML for recommendations, processing 1 billion views/day"]

**Query 2: "Explain supervised, unsupervised, reinforcement learning with industry applications"**  
Result: [300+ words with concrete examples: "Amazon uses unsupervised learning for customer segmentation"]


image_files:
- ml-types-diagram.jpg
```

**Query Template (use for detailed results):**
```
"Explain [TOPIC] including:
- Definition and key concepts
- 3-4 concrete examples with company/product names  
- Statistics, numbers, or market data
- Historical context or current trends"
```

**Key Requirements:**
- ✅ Include **specific names** (companies, products, people)
- ✅ Include **numbers** (percentages, dates, statistics)
- ✅ Include **examples** (3-5 concrete cases per major concept)
- ✅ Store **full detailed responses** (don't summarize, keep all details)

Run multiple SearchEnhancedQA.run calls in batch and store ALL results verbatim in todo.md

### A4. Batch Image Generation
- Review outline and identify which slides need images (typically: Cover, Content, Data slides)
- Plan suitable images for every slide, ensuring thematic consistency
- Generate ALL images using ImageCreator.generate_image (see "Image Processing Best Practices" section above for command format)
- Record actual generated filenames in todo.md

**Critical**: MUST complete all 4 steps before proceeding to Phase B.

---

## Phase B: Per-Slide Creation Loop

Repeat these steps for EACH slide sequentially (complete Slide 1 before starting Slide 2):

### B1. Design Slide Structure
Transform outline into concrete content structure:
- Define content hierarchy (title, subtitle, 2-4 supporting elements)
- Choose layout pattern from "Slide Structure Guidelines" section
- Map cached resources (search results, images) to slide elements
- Sketch content skeleton in todo.md

### B2. Build TSX Component
Create the slide file using:
- **Text content**: Use cached search results from Phase A3
- **Images**: Reference actual filenames from Phase A4 using `/assets/[filename]`
- **Charts**: Use Chart component with appropriate type and data
- **Layout**: Follow Design Guidelines (spacing, typography, color consistency)
- **Styling**: Ensure `h-full` on root `<section>`, proper gap/spacing values

**Example image reference:**
```tsx
<img src="/assets/ai-robot-collaboration.jpg" alt="AI Collaboration" className="..." />
```

### B3. Move to Next Slide
Mark current slide complete in todo.md, proceed to next slide.

---

### Execution Rules
- ❌ **NEVER** skip Phase A or start Phase B before completing Phase A
- ❌ **NEVER** work on multiple slides simultaneously - complete current slide before starting next
- ✅ **ALWAYS** verify image filenames match exactly what ImageCreator generated

---

## Phase C: Quality Assurance (Overflow Detection & Fix)

After completing ALL slides in Phase B, run this iterative detection-fix-verify loop until all issues are resolved.

### C1. Batch Fix (Recommended for AI Editors - ONE-SHOT)

**For AI agents/editors, use this streamlined workflow to fix ALL issues in one pass:**

1. **Run detection**: `pnpm run check-overflow` → generates `check_overflow.json`
2. **Read batch prompt**: `Editor.read("check_overflow.json")` → extract `batchFixPrompt` field
3. **Execute batch fixes**:
   - The `batchFixPrompt` contains a complete Markdown guide with:
     - Global fix strategies (spacing reduction, card merging, font size)
     - List of files to modify (sorted by priority: CRITICAL → HIGH → MEDIUM)
     - Specific actions for each file
     - Code examples and expected outcomes
   - **Apply all fixes in ONE batch** using `Editor.write`
   - Process files by priority order
4. **Verify**: `pnpm run check-overflow` → target: `totalViolations → 0`
5. **Iterate if needed**: If violations remain, repeat steps 1-4 (usually 1-2 iterations total)

**Key advantage**: Fixes 60-80% of violations in first pass vs. manual iterative fixing (10+ rounds).

**Example prompt for AI editor:**
```
Read check_overflow.json, extract the batchFixPrompt field, and execute 
all fixes according to its instructions. Apply changes to all listed files 
in one batch, then verify with pnpm run check-overflow.
```

### C2. Manual/Iterative Fix (Alternative)

For manual fixes or when fine-tuning specific slides:

1. **Run**: `pnpm run check-overflow` → generates `check_overflow.json`
2. **Read**: Check `totalViolations` count and console output
3. **Analyze** (if violations > 0):
   - **FIRST**: Check if HEIGHT_ANALYSIS shows card blocks and removal suggestions
   - Read the violation report and problematic slide file
   - Prioritize fixes based on the recommendation hierarchy below
4. **Fix**: Apply fixes in priority order (see C2 below)
5. **Verify**: Re-run detection (GOTO step 1)
6. **Exit** (if violations === 0): Quality check complete ✅

### C2. Fix Strategies by Priority (⭐⭐⭐ = Highest)

**Strategy 1: Reduce Card/Block Count** ⭐⭐⭐ **MOST RECOMMENDED**

| Action | When to Use | Effectiveness | Example |
|--------|-------------|---------------|---------|
| **Remove entire card/div blocks** | HEIGHT_ANALYSIS suggests removing N cards | **Best** - Saves 150-200px per card | 4 cards → 3 cards (save ~170px) |
| **Merge content** | Multiple similar cards exist | **Great** - Consolidates information | 2 feature cards → 1 combined card |

**Why this is best:**
- ✅ Directly removes large chunks of height (150-200px per card)
- ✅ Maintains visual quality - no compression needed
- ✅ Improves content focus - less is more
- ✅ One-time fix vs. adjusting multiple small values

**How to identify which cards to remove:**
- Check HEIGHT_ANALYSIS output for card list sorted by height
- Remove cards with least important information
- Consider merging 2-3 cards into 1 if content is related

---

**Strategy 2: Adjust Spacing/Sizing** ⭐⭐ (Use if Strategy 1 insufficient)

| Violation Type | Fix Strategy | Savings |
|---|---|---|
| **VERTICAL_OVERFLOW** | Reduce heights (`h-32`→`h-24`) + gaps (`gap-8`→`gap-6`) + padding (`p-8`→`p-6`) | 8-32px per change |
| **BODY_OVERFLOW** | Convert to grid (`grid grid-cols-2`) OR reduce spacing | Layout dependent |

---

**Strategy 3: Other Fixes** ⭐ (Edge cases only)

| Violation Type | Fix Strategy | When to Use |
|---|---|---|
| **HORIZONTAL_OVERFLOW** | Add `break-words`, reduce widths | Rare - text/code overflow |
| **MARGIN_VIOLATION** (Full Mode) | Add margin (`mt-12`, `mb-12`) | Only in full detection mode |
| **TEXT_TRUNCATION** (Full Mode) | Remove `truncate`, add `break-words` | Only in full detection mode |

### C3. Space Reduction Reference

**Priority 1: Remove Card Blocks** (Most Effective)

| Action | Savings | When to Apply |
|---|---|---|
| Remove 1 card block | **~170px** | HEIGHT_ANALYSIS suggests removing cards |
| Merge 2 cards into 1 | **~170px** | Similar content exists |
| Convert 4 vertical cards → 3 cards + grid | **~85px** | Can rearrange layout |

**Priority 2: Adjust Spacing/Sizing** (If card removal insufficient)

| Change | Savings per Element | Priority |
|---|---|---|
| `h-32` → `h-24` | 32px | ⭐⭐⭐ Highest |
| `gap-8` → `gap-6` | 8px per gap | ⭐⭐ High |
| `space-y-8` → `space-y-6` | 8px per gap | ⭐⭐ High |
| `p-8` → `p-6` | 16px (both sides) | ⭐⭐ High |
| `text-xl` → `text-lg` | 2px | ⭐ Low |

**Example Fix (Card Removal - Recommended):**
```typescript
// Detection Output:
// HEIGHT_ANALYSIS: 4 cards found, suggest removing 1 card
// BODY_OVERFLOW: overflowAmount: 130px

// Solution (Best): Remove 1 card
// Before: 4 feature cards (680px total)
// After:  3 feature cards (510px total)
// Saved:  170px ✅ Problem solved!
```

**Example Fix (Spacing Adjustment - Alternative):**
```typescript
// Detection: VERTICAL_OVERFLOW, overflowAmount: 15px
// Current: 4 cards with h-32, space-y-8

// Solution (compound fixes):
// 1. h-32 → h-28 = 16px saved
// 2. space-y-8 → space-y-6 = 8px saved 
```

### C4. Important Notes
- **Detection Mode**: System uses **Simple Mode** by default (HEIGHT_ANALYSIS + BODY_OVERFLOW + VERTICAL_OVERFLOW only)
- **Batch vs Iterative**: For AI editors, ALWAYS use batch fix (C1) for efficiency. Manual fixes (C2) are for human developers or fine-tuning
- **batchFixPrompt**: Auto-generated complete fix guide with file paths, priorities, and specific actions - USE THIS for one-shot fixes
- **Card Block Priority**: Always check HEIGHT_ANALYSIS first - if it suggests removing cards, do that before adjusting spacing
- **Always re-run detection** after each fix to verify success
- **Maximum 2-3 iterations**: With batch fixing, most issues resolve in 1-2 passes (vs. 10+ with manual)
- **Use targeted edits**: Never rewrite entire files
- **The detector runs automatically** during preview - you only need to fix reported violations

### C5. Critical Layout Pattern: space-y vs flex (⚠️ COMMON TRAP)
**Problem**: `flex-1` does NOT work in `space-y-*` containers (block layout). This causes image overflow.
#### Quick Fix
```tsx
// ✅ CORRECT: flex-1 works, image adapts
<div className="flex flex-col gap-4 min-h-0">
  <div><Chart height={200} /></div>
  <div className="flex-1 min-h-0">
    <img className="w-full h-full object-cover" />
  </div>
</div>
```
**Diagnosis**: If `elementPath` in `check_overflow.json` contains both `space-y-*` AND `flex-1`, replace `space-y-4` with `flex flex-col gap-4 min-h-0`.
**Rule**: Use `space-y-*` only when all children have fixed heights. Use `flex flex-col gap-*` for dynamic height distribution.

### C6. File Edit Tool Selection (For AI Agents)

**Decision Rule**:
- **1-2 line changes** → `edit_file_by_replace` (precise, clean diff)
- **3+ line changes** → `Editor.write` (reliable, handles complexity)

**Best Practices**:
1. `edit_file_by_replace` requires EXACT match (indentation, spaces)
2. Include 3-5 lines context in `old_string` for uniqueness
3. **ALWAYS verify** with `Editor.read` after ANY edit
4. If `edit_file_by_replace` fails twice, switch to `Editor.write`

**Example** (space-y → flex fix):
```typescript
// ✅ Good: Single line, exact match
old_string: '        <div className="space-y-4">'
new_string: '        <div className="flex flex-col gap-4 min-h-0">'
```

### C7. Detection Mode Reference

| Mode | Checks | Use Case |
|------|--------|----------|
| **Simple** (Default) | HEIGHT_ANALYSIS, BODY_OVERFLOW, VERTICAL_OVERFLOW | ✅ Recommended for 90% of cases |
| **Full** | All 7 checks including margins, horizontal, text truncation | Only for strict compliance |

**To switch to Full Mode** (rarely needed):
```tsx
<OverflowDetector detectionMode="full" />
```

## Common Issues & Reminders

1. **Animation Invalid** → Confirm whether in full screen preview mode
2. **Images not displaying** → Check filename spelling, extension matching (.jpg, .png), and verify files exist in `public/assets/` directory
3. **Image Usage Principles** → When ImageCreator generates image files, MUST use the actual filenames provided. Prohibit CSS placeholders - always generate real images using ImageCreator.generate_image.
4. **JSX Curly Braces in Text** → When displaying literal curly braces in text (e.g., mathematical sets like {a, b}), escape them using `{"{"}` and `{"}"}` to avoid JSX parsing errors.
5. **Overflow Batch Fixing** → For AI editors: ALWAYS use `batchFixPrompt` from check_overflow.json for one-shot fixes. Fixes 60-80% of issues in first pass.
6. **Overflow with Multiple Cards** → If HEIGHT_ANALYSIS detects 4+ cards and suggests removal, ALWAYS remove cards first before adjusting spacing. Removing 1 card saves ~170px instantly.
7. **Console Shows Card Recommendations** → Check browser console for detailed HEIGHT_ANALYSIS output with card statistics and removal suggestions during development.
8. **⚠️ Image Overflow with flex-1 Not Working** → If images overflow despite using `flex-1 min-h-0`, check the parent container. `flex-1` ONLY works in **flex containers** (`flex flex-col`), NOT in `space-y-*` containers (which use block layout). See Section C5 for detailed explanation and fix.

## Reference Files

### Core Components
- Register Decorator：`src/decorators/RegisterSlide.ts`
- Animation Hook：`src/hooks/useSlideAnimation.ts`
- Overflow Detector：`src/components/core/OverflowDetector.tsx`
- Example Component：`src/pages/slides/IntroSlide.tsx`

### Documentation
- **AI Editor Batch Fix**: `docs/AI_EDITOR_BATCH_FIX.md` - ⭐ ONE-SHOT fix guide for AI editors (RECOMMENDED)
- **System Architecture**: `docs/OVERFLOW_DETECTION_SYSTEM.md` - Complete system documentation
- **Simple Mode Guide**: `docs/SIMPLE_MODE_GUIDE.md` - Understanding simple vs. full detection modes
- **Height Analysis**: `docs/HEIGHT_ANALYSIS.md` - Detailed guide on card block analysis and height statistics
- **Overflow Fix Guide**: `docs/OVERFLOW_FIX_GUIDE.md` - Comprehensive strategies for fixing overflow issues with card removal emphasis

### Scripts
- Overflow Check：`pnpm run check-overflow` - Runs detection and generates JSON report with batchFixPrompt

## Your Task
Make sure to delete the example component `src/pages/slides/IntroSlide.tsx` and `src/pages/slides/end.tsx` before you begin coding.