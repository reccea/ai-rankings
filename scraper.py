#!/usr/bin/env python3
"""
AI Leaderboard Scraper
Fetches data from three sources:
1. Artificial Analysis Intelligence Index
2. SWE-Bench Verified
3. Humanity's Last Exam (HLE)

Usage:
    python scraper.py

Output:
    data.json - Standardized data in JSON format
"""

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re


class AILoaderboardScraper:
    def __init__(self):
        self.data = {
            "intelligenceIndex": [],
            "swebench": [],
            "hle": [],
            "lastUpdate": datetime.now().isoformat(),
            "sources": {
                "artificialAnalysis": "https://artificialanalysis.ai",
                "swebench": "https://www.swebench.com",
                "hle": "https://artificialanalysis.ai/evaluations/humanitys-last-exam"
            }
        }

    async def scrape_artificial_analysis(self):
        """Scrape Intelligence Index from Artificial Analysis"""
        print("Scraping Artificial Analysis Intelligence Index...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # Go to the page
                await page.goto("https://artificialanalysis.ai/#artificial-analysis-intelligence-index", wait_until="networkidle")
                await asyncio.sleep(3)  # Wait for dynamic content

                # Get page content
                content = await page.content()
                await browser.close()

                # Parse HTML
                soup = BeautifulSoup(content, 'html.parser')

                # Look for table or grid data
                # The data is typically in a table or div grid
                tables = soup.find_all('table')

                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 2:
                            # Try to extract model name and score
                            name = cols[0].get_text(strip=True)
                            # Look for score in various columns
                            for col in cols[1:]:
                                text = col.get_text(strip=True)
                                # Check if it looks like a score
                                try:
                                    score = float(text)
                                    if 0 < score < 100:
                                        if name and not any(x in name.lower() for x in ['rank', 'model', 'elo', 'score']):
                                            self.data["intelligenceIndex"].append({
                                                "name": name,
                                                "provider": self._extract_provider(name),
                                                "score": score
                                            })
                                except:
                                    continue

                print(f"Found {len(self.data['intelligenceIndex'])} models from Artificial Analysis")
        except Exception as e:
            print(f"Error scraping Artificial Analysis: {e}")
            # Use fallback data
            self.data["intelligenceIndex"] = self._fallback_intelligence_index()

    async def scrape_swebench(self):
        """Scrape SWE-Bench Verified leaderboard"""
        print("Scraping SWE-Bench Verified...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto("https://www.swebench.com/", wait_until="networkidle")
                await asyncio.sleep(3)

                content = await page.content()
                await browser.close()

                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.find_all('table')

                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 2:
                            name = cols[0].get_text(strip=True)
                            for col in cols[1:]:
                                text = col.get_text(strip=True)
                                # SWE-Bench scores are percentages like "74.40%"
                                match = re.search(r'(\d+\.?\d*)%?', text)
                                if match:
                                    score = float(match.group(1))
                                    if 0 < score <= 100:
                                        if name and not any(x in name.lower() for x in ['rank', 'model', '%', 'resolved']):
                                            self.data["swebench"].append({
                                                "name": name,
                                                "provider": self._extract_provider(name),
                                                "score": score
                                            })

                print(f"Found {len(self.data['swebench'])} models from SWE-Bench")
        except Exception as e:
            print(f"Error scraping SWE-Bench: {e}")
            self.data["swebench"] = self._fallback_swebench()

    async def scrape_hle(self):
        """Scrape Humanity's Last Exam leaderboard"""
        print("Scraping Humanity's Last Exam...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto("https://artificialanalysis.ai/evaluations/humanitys-last-exam", wait_until="networkidle")
                await asyncio.sleep(3)

                content = await page.content()
                await browser.close()

                soup = BeautifulSoup(content, 'html.parser')
                tables = soup.find_all('table')

                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows[1:]:
                        cols = row.find_all(['td', 'th'])
                        if len(cols) >= 2:
                            name = cols[0].get_text(strip=True)
                            for col in cols[1:]:
                                text = col.get_text(strip=True)
                                # HLE scores are percentages
                                match = re.search(r'(\d+\.?\d*)%?', text)
                                if match:
                                    score = float(match.group(1))
                                    if 0 < score <= 100:
                                        if name and not any(x in name.lower() for x in ['rank', 'model', 'accuracy', 'score']):
                                            self.data["hle"].append({
                                                "name": name,
                                                "provider": self._extract_provider(name),
                                                "score": score
                                            })

                print(f"Found {len(self.data['hle'])} models from HLE")
        except Exception as e:
            print(f"Error scraping HLE: {e}")
            self.data["hle"] = self._fallback_hle()

    def _extract_provider(self, name):
        """Extract provider from model name"""
        name_lower = name.lower()
        if 'claude' in name_lower:
            return 'Anthropic'
        elif 'gpt' in name_lower or 'openai' in name_lower:
            return 'OpenAI'
        elif 'gemini' in name_lower or 'google' in name_lower:
            return 'Google'
        elif 'kimi' in name_lower or 'moonshot' in name_lower:
            return 'Moonshot AI'
        elif 'glm' in name_lower:
            return 'Z AI'
        elif 'qwen' in name_lower:
            return 'Alibaba'
        elif 'deepseek' in name_lower:
            return 'DeepSeek'
        elif 'minimax' in name_lower:
            return 'Minimax'
        elif 'llama' in name_lower or 'meta' in name_lower:
            return 'Meta'
        elif 'mistral' in name_lower:
            return 'Mistral'
        else:
            return 'Unknown'

    def _fallback_intelligence_index(self):
        """Fallback data for Intelligence Index"""
        return [
            {"name": "Claude Opus 4.6 (max)", "provider": "Anthropic", "score": 53.03},
            {"name": "Claude Sonnet 4.6 (max)", "provider": "Anthropic", "score": 51.27},
            {"name": "GPT-5.2 (xhigh)", "provider": "OpenAI", "score": 51.24},
            {"name": "Claude Opus 4.5", "provider": "Anthropic", "score": 49.69},
            {"name": "GLM-5", "provider": "Z AI", "score": 49.64},
            {"name": "GPT-5.2 Codex (xhigh)", "provider": "OpenAI", "score": 48.98},
            {"name": "Gemini 3 Pro Preview (high)", "provider": "Google", "score": 48.44},
            {"name": "GPT-5.1 (high)", "provider": "OpenAI", "score": 47.56},
            {"name": "Kimi K2.5", "provider": "Moonshot AI", "score": 46.73},
            {"name": "GPT-5.2 (medium)", "provider": "OpenAI", "score": 46.58},
            {"name": "Gemini 3 Flash", "provider": "Google", "score": 46.40},
        ]

    def _fallback_swebench(self):
        """Fallback data for SWE-Bench"""
        return [
            {"name": "Claude 4.5 Opus medium (20251101)", "provider": "Anthropic", "score": 74.40},
            {"name": "Gemini 3 Pro Preview (2025-11-18)", "provider": "Google DeepMind", "score": 74.20},
            {"name": "GPT-5.2 (2025-12-11) (high reasoning)", "provider": "OpenAI", "score": 71.80},
            {"name": "Claude 4.5 Sonnet (20250929)", "provider": "Anthropic", "score": 70.60},
            {"name": "GPT-5.2 (2025-12-11)", "provider": "OpenAI", "score": 69.00},
            {"name": "Claude 4 Opus (20250514)", "provider": "Anthropic", "score": 67.60},
            {"name": "GPT-5.1-codex (medium reasoning)", "provider": "OpenAI", "score": 66.00},
            {"name": "GPT-5.1 (2025-11-13) (medium reasoning)", "provider": "OpenAI", "score": 66.00},
            {"name": "GPT-5 (2025-08-07) (medium reasoning)", "provider": "OpenAI", "score": 65.00},
            {"name": "Claude 4 Sonnet (20250514)", "provider": "Anthropic", "score": 64.93},
        ]

    def _fallback_hle(self):
        """Fallback data for HLE"""
        return [
            {"name": "Gemini 3 Pro Preview", "provider": "Google", "score": 37.52},
            {"name": "Claude Opus 4.6 (Thinking Max)", "provider": "Anthropic", "score": 34.44},
            {"name": "GPT-5 Pro (2025-10-06)", "provider": "OpenAI", "score": 31.64},
            {"name": "GPT-5.2 (2025-12-11)", "provider": "OpenAI", "score": 27.80},
            {"name": "GPT-5 (2025-08-07)", "provider": "OpenAI", "score": 25.32},
            {"name": "Claude Opus 4.5 Thinking", "provider": "Anthropic", "score": 25.20},
            {"name": "Kimi K2.5", "provider": "Moonshot AI", "score": 24.37},
            {"name": "GPT-5.1 Thinking", "provider": "OpenAI", "score": 23.68},
            {"name": "Gemini 2.5 Pro Preview", "provider": "Google", "score": 21.64},
            {"name": "o3 (high) (April 2025)", "provider": "OpenAI", "score": 20.32},
        ]

    async def run(self):
        """Run all scrapers"""
        print("=" * 50)
        print("AI Leaderboard Scraper")
        print("=" * 50)

        await self.scrape_artificial_analysis()
        await self.scrape_swebench()
        await self.scrape_hle()

        # Sort each list by score
        self.data["intelligenceIndex"].sort(key=lambda x: x["score"], reverse=True)
        self.data["swebench"].sort(key=lambda x: x["score"], reverse=True)
        self.data["hle"].sort(key=lambda x: x["score"], reverse=True)

        # Save to JSON
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        print("=" * 50)
        print(f"Scraping complete!")
        print(f"Intelligence Index: {len(self.data['intelligenceIndex'])} models")
        print(f"SWE-Bench: {len(self.data['swebench'])} models")
        print(f"HLE: {len(self.data['hle'])} models")
        print(f"Data saved to data.json")
        print("=" * 50)

        return self.data


async def main():
    scraper = AILoaderboardScraper()
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
