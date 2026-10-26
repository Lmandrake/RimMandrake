Windows chrome.exe --headless --window-size=390,... does NOT render at 390 px: headless Chrome clamps the layout viewport to a minimum of ~526 px wide, so a 'phone' screenshot is really a 526-px tablet and phone-layout bugs (wrapping, flex overflow) are invisible. For phone width use Playwright with viewport width 390 (or device emulation).
home: visual-render-qa
