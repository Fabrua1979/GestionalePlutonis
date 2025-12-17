#!/usr/bin/env python3
"""
Auto-collect overflow reports after build

This script:
1. Starts a Vite dev server
2. Opens the presentation in headless browser (reusing server's Browser service)
3. Navigates through all slides
4. Extracts overflow reports from window object
5. Saves to check_overflow.json
"""

import asyncio
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional
from metagpt.tools.libs.browser import Browser

# Add MetaGPT to Python path to reuse Browser service
metagpt_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(metagpt_root))



def find_slide_file(slide_title: str, project_dir: Path) -> Optional[str]:
    """
    Find slide file path based on slide title
    Supports Chinese/English mixed titles by reading RegisterSlide decorators
    """
    slides_dir = project_dir / "src" / "pages" / "slides"
    if not slides_dir.exists():
        return None
    
    # Strategy 1: Read files and match RegisterSlide title
    for file_path in slides_dir.glob("*.tsx"):
        try:
            content = file_path.read_text(encoding='utf-8')
            # Extract title from RegisterSlide({ title: "xxx", ... })
            match = re.search(r'RegisterSlide\s*\(\s*\{[^}]*title\s*:\s*["\']([^"\']+)["\']', content)
            if match and match.group(1) == slide_title:
                return f"src/pages/slides/{file_path.name}"
        except Exception:
            continue
    
    # Strategy 2: Extract English part and do keyword matching (fallback)
    english_part = re.sub(r'[^\x00-\x7F]+', ' ', slide_title).strip()
    normalized = re.sub(r'[^a-zA-Z0-9\s]', ' ', english_part).strip().lower()
    keywords = [w for w in normalized.split() if len(w) > 2]
    
    if not keywords:
        return None
    
    # Try to match files with scoring system
    best_match = None
    best_score = 0
    
    for file_path in slides_dir.glob("*.tsx"):
        filename = file_path.stem.lower()
        filename_without_slide = filename.replace('slide', '')
        
        # Exact match
        normalized_compact = normalized.replace(' ', '')
        if normalized_compact and (filename_without_slide == normalized_compact or filename == normalized_compact):
            return f"src/pages/slides/{file_path.name}"
        
        # Keyword matching with scoring
        score = sum(len(keyword) for keyword in keywords if keyword in filename)
        
        # Check common slide name patterns
        if keywords:
            title_pattern = ''.join(w.capitalize() for w in keywords)
            if title_pattern.lower() in filename:
                score += len(title_pattern) * 2
        
        if score > best_score:
            best_score = score
            best_match = file_path.name
    
    return f"src/pages/slides/{best_match}" if best_match and best_score > 0 else None


def generate_fix_suggestions(violation: Dict) -> Dict:
    """Generate fix suggestions based on violation type"""
    v_type = violation.get('type')
    message = violation.get('message', '')
    overflow_amount = violation.get('overflowAmount', 0)
    actual = violation.get('actual', 0)
    expected = violation.get('expected', 0)
    
    strategies = {
        'CONTAINER_OVERFLOW': {
            'priority': 'HIGH',
            'fixSuggestions': [
                {
                    'strategy': 'Remove overflow:hidden',
                    'description': 'Change parent container from overflow:hidden to allow content to show',
                    'codePattern': 'overflow-hidden',
                    'suggestedChange': 'Remove overflow-hidden class OR change to overflow-auto',
                    'risk': 'LOW',
                    'estimatedFix': f'Will reveal {round(overflow_amount)}px of hidden content',
                },
                {
                    'strategy': 'Reduce content',
                    'description': f'Remove ~{round(overflow_amount)}px worth of content',
                    'suggestedChange': 'Remove 1-2 cards, reduce padding/gaps, or shorten text',
                    'risk': 'MEDIUM',
                    'estimatedFix': f'Need to save {round(overflow_amount)}px',
                },
            ],
        },
        'VERTICAL_OVERFLOW': {
            'priority': 'HIGH' if 'compressed' in message or 'squeezed' in message else 'MEDIUM',
            'fixSuggestions': [
                {
                    'strategy': 'Optimize content density',
                    'description': 'Adjust content to fill available space without compression',
                    'suggestedChange': f'Card needs {round(actual)}px but only gets {round(expected)}px',
                    'risk': 'LOW',
                    'estimatedFix': f'Need to save {round(overflow_amount)}px or expand container',
                },
            ],
        },
        'BODY_OVERFLOW': {
            'priority': 'CRITICAL',
            'fixSuggestions': [
                {
                    'strategy': 'Remove content blocks',
                    'description': 'Primary solution: delete entire cards/sections',
                    'suggestedChange': f'Remove 1-2 card blocks (saves ~170px each)',
                    'risk': 'MEDIUM',
                    'estimatedFix': f'Need to save {round(overflow_amount)}px total',
                },
                {
                    'strategy': 'Reduce spacing',
                    'description': 'Compact the layout',
                    'suggestedChange': 'Reduce: gap-8→gap-4, p-8→p-6, space-y-8→space-y-4',
                    'risk': 'MEDIUM',
                    'estimatedFix': f'Save 8-16px per change (need {round(overflow_amount / 12)} changes)',
                },
            ],
        },
    }
    
    return strategies.get(v_type, {
        'priority': 'MEDIUM',
        'fixSuggestions': [
            {
                'strategy': 'Manual review',
                'description': message,
                'suggestedChange': 'Review the violation and adjust accordingly',
                'risk': 'UNKNOWN',
            }
        ],
    })


def enhance_report_for_ai_editor(report: Dict, project_dir: Path) -> Dict:
    """Enhance overflow report with AI-friendly information"""
    if not report or 'reports' not in report:
        return report
    
    enhanced_reports = []
    for slide_report in report['reports']:
        # Find the slide file
        slide_file = find_slide_file(slide_report['slideTitle'], project_dir)
        
        # Group violations by type
        violations_by_type = {}
        for violation in slide_report.get('violations', []):
            v_type = violation['type']
            if v_type not in violations_by_type:
                violations_by_type[v_type] = []
            violations_by_type[v_type].append(violation)
        
        # Generate fix suggestions
        fix_suggestions = {}
        for v_type, violations in violations_by_type.items():
            first_violation = violations[0]
            suggestions = generate_fix_suggestions(first_violation)
            fix_suggestions[v_type] = {
                'count': len(violations),
                'priority': suggestions['priority'],
                'strategies': suggestions['fixSuggestions'],
                'affectedElements': [v.get('elementInfo') or v.get('element') for v in violations[:3] if v.get('elementInfo') or v.get('element')],
            }
        
        # Determine highest priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        highest_priority = min(
            (suggestions.get('priority', 'MEDIUM') for suggestions in fix_suggestions.values()),
            key=lambda p: priority_order.get(p, 999),
            default='MEDIUM'
        )
        
        enhanced_reports.append({
            **slide_report,
            'slideFile': slide_file or 'Unknown - check src/pages/slides/',
            'fixSuggestions': fix_suggestions,
            'aiEditorNotes': {
                'totalIssues': len(slide_report.get('violations', [])),
                'highestPriority': highest_priority,
                'recommendedAction': list(fix_suggestions.values())[0]['strategies'][0]['strategy'] if fix_suggestions else 'Review manually',
            },
        })
    
    return {
        **report,
        'reports': enhanced_reports,
        'aiEditorInstructions': {
            'workflow': [
                '1. Read this file to understand all overflow issues',
                '2. For each slide report, check the slideFile path',
                '3. Read the slide file',
                '4. Review fixSuggestions for each violation type',
                '5. Apply the lowest-risk fix strategy first',
                '6. Re-run: pnpm run check-overflow to verify',
                '7. Iterate until totalViolations === 0',
            ],
            'priorityOrder': 'CRITICAL → HIGH → MEDIUM → LOW',
            'maxIterations': 3,
            'criticalNote': 'ALWAYS fix CRITICAL and HIGH priority issues. Use card removal first (saves most space).',
        },
    }


async def collect_overflow_reports(project_dir: Path) -> Dict:
    """Main function to collect overflow reports"""
    print('🚀 Starting automatic overflow detection...')
    print(f'   Project: {project_dir}\n')
    
    # Start Vite dev server
    print('📦 Starting Vite dev server...')
    vite_process = subprocess.Popen(
        ['pnpm', 'dev', '--port', '0'],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Extract port from output
    preview_url = None
    try:
        for line in vite_process.stdout:
            print(f'   {line.rstrip()}')
            match = re.search(r'http://localhost:(\d+)', line)
            if match:
                preview_url = f'http://localhost:{match.group(1)}'
                break
            # Timeout after 30 seconds
            if vite_process.poll() is not None:
                raise Exception('Vite server failed to start')
        
        if not preview_url:
            # Wait a bit more
            await asyncio.sleep(5)
            preview_url = 'http://localhost:5173'
        
        print(f'✅ Server started at: {preview_url}\n')
        
        # Launch headless browser using server's Browser service
        print('🌐 Launching headless browser...')
        browser = Browser(headless=True)
        await browser.start()
        
        try:
            # Navigate to the presentation
            print('📄 Loading presentation...')
            await browser.goto(preview_url, timeout=60000)
            
            # Wait for React to initialize
            await asyncio.sleep(3)
            
            # Get total slides
            slide_count = await browser.page.evaluate('''
                () => {
                    const slides = window.__allSlides || [];
                    return slides.length;
                }
            ''')
            
            if slide_count == 0:
                print('⚠️  Could not detect slides, waiting longer...')
                await asyncio.sleep(3)
                slide_count = await browser.page.evaluate('''
                    () => {
                        const slides = window.__allSlides || [];
                        return slides.length;
                    }
                ''')
            
            print(f'📊 Total slides: {slide_count}\n')
            
            if slide_count == 0:
                raise Exception('No slides detected in presentation')
            
            # Navigate through all slides
            print('🔄 Navigating through slides to trigger detection...')
            for i in range(slide_count):
                print(f'   Slide {i + 1}/{slide_count}')
                
                if i > 0:
                    # Use the exposed __navigateToSlide function
                    navigated = await browser.page.evaluate(f'''
                        (slideIndex) => {{
                            if (typeof window.__navigateToSlide === 'function') {{
                                return window.__navigateToSlide(slideIndex);
                            }}
                            return false;
                        }}
                    ''', i)
                    
                    if not navigated:
                        print(f'   ⚠️  Could not navigate to slide {i + 1}')
                    
                    await asyncio.sleep(0.8)
                else:
                    await asyncio.sleep(1)
            
            # Wait for final detection
            print('\n⏳ Waiting for final detection to complete...')
            await asyncio.sleep(2)
            
            # Generate summary
            print('📥 Generating final overflow summary...')
            overflow_summary = await browser.page.evaluate('''
                () => {
                    if (typeof window.__generateOverflowSummary === 'function') {
                        return window.__generateOverflowSummary();
                    }
                    return window.__overflowSummary;
                }
            ''')
            
            # Enhance report
            if not overflow_summary:
                final_report = {
                    'generatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'totalSlides': slide_count,
                    'slidesWithIssues': 0,
                    'totalViolations': 0,
                    'reports': [],
                    'aiEditorInstructions': {
                        'message': 'No overflow issues detected! All slides fit within bounds.',
                    },
                }
            else:
                final_report = enhance_report_for_ai_editor(overflow_summary, project_dir)
            
            # Save to file
            output_path = project_dir / 'check_overflow.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, indent=2, ensure_ascii=False)
            
            # Print summary
            if final_report['totalViolations'] == 0:
                print('\n✅ No overflow issues detected!')
            else:
                print('\n📋 Summary:')
                print(f'   Total Slides: {final_report["totalSlides"]}')
                print(f'   Slides with Issues: {final_report["slidesWithIssues"]}')
                print(f'   Total Violations: {final_report["totalViolations"]}')
                
                print('\n🚨 Violations found:')
                for report in final_report['reports']:
                    if report.get('violations'):
                        print(f'\n   Slide {report["slideIndex"] + 1}: {report["slideTitle"]}')
                        if report.get('slideFile'):
                            print(f'      File: {report["slideFile"]}')
                        for v in report['violations']:
                            print(f'      - [{v["type"]}] {v["message"]}')
            
            print(f'\n💾 Report saved to: {output_path}')
            
            return final_report
            
        finally:
            await browser.stop()
            print('\n🧹 Cleanup completed')
    
    finally:
        # Cleanup Vite process
        if vite_process:
            vite_process.terminate()
            try:
                vite_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                vite_process.kill()


def main():
    """Main entry point"""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    try:
        result = asyncio.run(collect_overflow_reports(project_dir))
        print('\n✨ Done!')
        sys.exit(0)
    except Exception as e:
        print(f'\n💥 Failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

