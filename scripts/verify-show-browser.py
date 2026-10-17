"""Read-only, manifest-bound browser playback QA; never publishes or ear-checks."""
import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs

from playwright.async_api import async_playwright


async def run(base, output):
    output = Path(output)
    assert not output.exists(), "Preserve earlier browser evidence; use a new output"
    manifest = json.loads(Path("docs/releases/show-media-current.json").read_text())
    checks = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        try:
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            response = await page.goto(urljoin(base, "/show"), wait_until="domcontentloaded")
            assert response.status == 200
            cards = page.locator(".atl-now-card")
            if manifest["expectedHub"]["currentPreview"]:
                assert await cards.nth(0).get_attribute("href") == manifest["expectedHub"]["currentPreview"]
                assert "this week" in (await cards.nth(0).inner_text()).lower()
            assert await cards.nth(1).get_attribute("href") == manifest["expectedHub"]["latestEpisode"]
            assert "latest episode" in (await cards.nth(1).inner_text()).lower()
            archive = page.locator("details")
            await archive.evaluate_all("els => els.forEach(el => el.open = true)")
            for route in manifest["expectedHub"]["pastPreviews"]:
                assert await page.locator(f'details a[href="{route}"]').count() > 0
            print("Hub current/latest/archive slots verified", flush=True)
            for item in manifest["media"]:
                for route in item["watchRoutes"]:
                    response = await page.goto(urljoin(base, route), wait_until="domcontentloaded")
                    assert response.status == 200
                    await page.wait_for_function("document.querySelector('video')?.readyState >= 1", timeout=45000)
                    video = page.locator("video")
                    info = await video.evaluate("v => ({src:v.currentSrc,duration:v.duration,width:v.videoWidth,height:v.videoHeight,tracks:v.querySelectorAll('track').length})")
                    src = urlparse(info["src"])
                    assert src.path == item["video"] and parse_qs(src.query)["v"] == [item["version"]]
                    assert abs(info["duration"] - item["seconds"]) < 0.2
                    assert info["width"] == 1280 and info["height"] == 720
                    if item["captionsBurnedIn"]:
                        assert info["tracks"] == 0, "Do not duplicate burned-in captions"
                    await video.evaluate("v => {v.muted=true; return v.play();}")
                    await page.wait_for_function("document.querySelector('video').currentTime > 0.6", timeout=15000)
                    target = min(200, info["duration"] * 0.6)
                    await video.evaluate("(v,t) => {v.pause(); v.currentTime=t;}", target)
                    await page.wait_for_function("t => {const v=document.querySelector('video');return !v.seeking && v.readyState>=2 && Math.abs(v.currentTime-t)<0.25}", arg=target, timeout=30000)
                    await video.evaluate("v => v.play()")
                    await page.wait_for_function("t => document.querySelector('video').currentTime > t+0.6", arg=target, timeout=15000)
                    playback = await video.evaluate("v => ({time:v.currentTime,paused:v.paused,error:v.error?.code??null,presentedFrames:v.getVideoPlaybackQuality().totalVideoFrames})")
                    assert playback["error"] is None and not playback["paused"] and playback["presentedFrames"] > 0
                    await video.evaluate("v => v.pause()")
                    checks.append({"id": item["id"], "route": route, **info, "played": True, "seekTarget": target, "seekAndResume": True, **playback})
                    print(f"Playback/seek/resume verified: {route}", flush=True)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps({"checkedAt": datetime.now(timezone.utc).isoformat(), "base": base,
                                          "releaseId": manifest["releaseId"], "hubSlotsAndArchive": True,
                                          "checks": checks, "mutedAutomatedPlayback": True,
                                          "notHumanAudioListening": True, "releaseApproved": manifest["releaseApproved"],
                                          "deploymentApproved": manifest["deploymentApproved"]}, indent=2) + "\n")
        finally:
            await browser.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("output")
    args = ap.parse_args()
    asyncio.run(run(args.base, args.output))
