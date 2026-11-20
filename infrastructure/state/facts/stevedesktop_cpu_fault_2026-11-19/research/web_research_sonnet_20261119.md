# Web research: replacement CPU options for SteveDesktop (Sonnet helper, 2026-11-19 ~11:50 PM PST)

Unverified by a second reader. Machine: i9-10900K (9 of 10 cores active), ASUS ROG STRIX Z490-G GAMING (WI-FI) BIOS 3401 (release date read from the machine: 2026-05-26), 4 x 32 GB DDR4-2666, RTX 2080 Ti.

1. REPLACEMENT CPUs FOR THE Z490-G
- ASUS's CPU-support page for this board (fetched through a summarizer) lists no 11th gen. It tops out at 10th gen (i9-10900K, i7-10700K), with validated BIOS 0403 to 2103. [found: https://www.asus.com/us/supportonly/rog%20strix%20z490-g%20gaming%20(wi-fi)/helpdesk_cpu/]
- The ASUS BIOS page fetch showed only 1003 (2020/12/23, adds Resizable BAR) and no 11th-gen note. Your BIOS 3401 is not verified by anything I found; the BIOS fetches were unreliable.
- A Tom's Hardware reply (Apr 2021) said an i7-11700 was not supported on this board. [found: https://forums.tomshardware.com/threads/will-an-i7-11700-work-with-a-rog-strix-z490-g-gaming.3699196]
- Intel says some Z490 boards need a BIOS update for 11th gen. [found: https://www.intel.com/content/www/us/en/support/articles/000058324.html]
- ASUS did add 11th-gen BIOSes to sibling boards (Z490-E 2004, Jan 2021; TUF Z490-PLUS 2210). [found: https://www.asus.com/us/supportonly/rog%20strix%20z490-e%20gaming/helpdesk_bios/]
- Z490-G minimum 11th-gen BIOS: not found. Treat 11th gen as unsupported on this board unless ASUS's table proves otherwise.
- Rocket Lake on Z490: PCIe 4.0 was GPU-slot only in ASUS testing, and the M.2 slots lacked Gen 4. That does not matter on a 2080 Ti, which is PCIe 3.0. [found: https://wccftech.com/asus-z490-motherboards-tested-intel-rocket-lake-desktop-cpu-lack-pcie-gen-4-0-support/]
- Intel lists DDR4-3200 at 1:1 only for the i9-K/KF parts; other 11th-gen SKUs run it at 2:1. 4 DIMMs need matched modules. [found: Anandtech/Notebookcheck results]
- 128 GB on the 11th-gen memory controller: not found. Rocket Lake is no faster at RimWorld and gains nothing for stability, so I would not pursue it.
- i9-10900K used: $261 (listed-used estimate from eBay completed sales, getpcparts, 2026-11-14). The 30-day average is $266 and the 90-day average is $275. A tested unit with returns is listed at $247-260. [found: https://www.getpcparts.com/market-prices/cpu-processors/intel-core-i9-10900k]
- eBay asks run about $240-420 (listed-used). Examples are $239.99 and $269.95. [found: https://www.ebay.com/shop/intel-10900k?_nkw=intel+10900k]
- i9-10900K new: Newegg boxed $424.00 and tray $398.66 (aggregator, undated). Amazon $529 (PCPartPicker, undated). eBay "factory sealed" $399.99 (listed-new). Current stock: not found. [found: https://pcpartpicker.com/product/cwFKHx/intel-core-i9-10900k-37-ghz-10-core-processor-bx8070110900k]
- i7-10700K used: about $178.99 (sold-price, 6 sales, PCPartValue) to $185 (getpcparts, Nov 2026). [found: https://pcpartvalue.com/cpu/intel-core-i7-10700k]
- i7-11700K used about $175 and i9-11900K used about $254 (getpcparts estimates, Nov 2026). [found: https://www.getpcparts.com/market-prices/cpu-processors]
- Not found at all: i9-10850K, 10900F/10900KF, i5-11600K, and any Micro Center, B&H, r/hardwareswap, Amazon Renewed or Newegg refurbished prices.
- Best drop-in: an i7-10700K or i9-10900 class chip, or a tested 10900K. A 10700K is lower power and cheaper, and it matches RimWorld's single-thread need. [guess ~70%]

2. WARRANTY
- Intel boxed processors typically carry a 3-year limited warranty from the original purchase date. Some carry 1 year. The period does not reset on replacement. [found: https://www.intel.com/content/www/us/en/support/articles/000005494/processors.html]
- I did not find a page confirming the 10900K's term specifically.
- A 2020 chip is almost certainly out of warranty. Check the batch/FPO and serial at supporttickets.intel.com/warrantyinfo. [found: same Intel page]
- The extra 2 years covers only 13th/14th gen affected by Vmin Shift, so it does not cover 10th gen. [found: same Intel page]
- No report found of Intel replacing an out-of-warranty 10th-gen chip. The RMA stories I found are all 13th/14th gen. [found: https://www.tomshardware.com/pc-components/cpus/intel-customer-scores-core-i9-14900k-as-a-replacement-for-degraded-core-i9-13900k-another-received-a-dollar599-check-for-a-fully-working-core-i9-13900k]
- Intel gives no warranty on used, refurbished or engineering-sample chips. [found: https://pcgamer.com/hardware/processors/intel-extends-its-warranty-support-for-13th-and-14th-gen-cpus-by-two-years-but-its-rma-procedure-has-been-anything-but-straightforward-for-some]

3. DIAGNOSIS
- Search found no evidence of a known 10th-gen degradation epidemic. Reports tie instability to voltage, load-line and board settings. [found: https://www.tomshardware.com/reviews/intel-core-i9-10900k-cpu-review/3]
- Searches for r/intel, r/buildapc, overclock.net and LTT threads on 10900K faults returned nothing usable. I have no forum evidence on board versus CPU versus RAM frequency.
- General practice, not sourced [guess ~60%]:
  - Per-core Prime95 errors with heat ruled out point at the CPU, but a VRM, socket-pin or RAM fault can mimic it.
  - Re-run with 2 DIMMs (64 GB) and then 4 DIMMs. Run MemTest86 for several passes.
  - Run Prime95 with affinity pinned per core.
  - Check the socket for bent pins and reseat the cooler.
  - Run Prime95 at stock (no XMP, no overclock, default load line) to see whether the errors stay.
  - The swap test is decisive: put the CPU in another LGA1200 board, or put a known-good 10th-gen CPU in yours.
- Intel community advice for a single bad core is to find it with Prime95 small FFTs and lower that core's ratio. That is a workaround, not a fix. [found: https://community.intel.com:443/t5/Processors/Can-anyone-verify-if-my-P-core-3-is-defected-i9-14900K/td-p/1621029]
- Used-CPU risks (delidded, heavily overclocked, hidden degradation): no sourced data. Buy from sellers with returns and run Prime95 on arrival. [guess ~65%]

4. PLATFORM REPLACEMENT (keeps 128 GB DDR4 and the 2080 Ti)
- (a) AM4:
  - 5800X3D: Amazon $339.95 (2026-11-19, tracker, lowest offer $319.99). Micro Center was $279.99 on 2026-11-06, with the regular price $349.99. Newegg $319.99 with a promo code, from $348.99. [found: https://borecraft.com/2026/11/08/the-ryzen-7-5800x3d-drops-to-just-279-its-lowest-price-since-amd-re-launched-the-chip/] (all listed-new)
  - 5700X: $133 (PassMark tracker, Nov 17) versus $178-225 (Amazon ranges). The $133 looks too low to trust. [found: https://www.cpubenchmark.net/compare/4814vs3870/AMD-Ryzen-7-5700X-vs-AMD-Ryzen-9-5900X]
  - 5900XT: Newegg $289.99 on sale, but it appeared backordered. [found: https://www.newegg.com/amd-ryzen-9-5000-series-ryzen-9-5900xt-vermeer-socket-am4-desktop-cpu-processor/p/N82E16819113845]
  - 5700X3D: no reliable price found.
  - B550 boards: price not found.
  - 4x32 GB on B550 Ryzen 5000 is hit and miss. Some run DDR4-3200 stable, others see WHEA errors and idle reboots. Expect to drop to 2933-3200 and tune voltages. [found: https://techpowerup.com/forums/threads/what-did-you-have-to-do-to-get-128gb-ram-working-on-zen3-cpu.301112/page-3]
- (b) LGA1700 with a DDR4 board:
  - B760 DDR4 boards: $80-170 (Newegg search page, undated). [found: https://www.newegg.com/p/pl?d=b760+motherboard+ddr4]
  - Micro Center bundle (i5-12600KF + MSI B760-P WiFi D4 + 1 TB SSD): $381.14 on Amazon, undated. [found: https://www.amazon.com/Micro-Center-Bundle-i5-12600KF-Motherboard/dp/B0DHXKC3J6]
  - Current standalone prices for 12600K, 14600K and 12700K: not found.
  - The 12th-gen 12600K/12700K avoid the 13th/14th-gen Vmin degradation risk. A 14600K carries it and has Intel's 2-year extension; I did not verify its current warranty status. [found: https://www.intel.com/content/www/us/en/support/articles/000005494/processors.html]
  - 128 GB on LGA1700 DDR4 boards: not verified.
- Best for single-thread work: a 12600K/12700K (Golden Cove) beats Skylake-derived chips and the 5800X3D probably wins on RimWorld's cache-heavy simulation. I found no benchmark; this is [guess ~60%].
- Best for stability: 12th gen on an ASUS/MSI B760 DDR4 board, or the 5800X3D, at 3200 or below. [guess ~55%]
- (c) DDR5: a 32 GB kit is about $430-600 (2026-11-16) and the cheapest DDR6000 kit was $438 on 11-12 (listed-new). 128 GB DDR5 would add roughly $1,700 or more, extrapolated, not found. Your DDR4 is the valuable part. [found: https://capitalandcompute.net/memory-prices/ddr5/]
- Retail DDR4 32 GB (2x16 GB, 3200) was $199.99 on Nov 10 (listed-new). A 128 GB DDR4 set is therefore roughly $800, my estimate from that price. [found: https://bottleneckpc.com/blog/best-ram-deals]

5. RANKED RECOMMENDATION (totals are estimates from the prices above)
1. Cheapest sound fix: run the swap and RAM tests first (about $0). If the CPU is at fault, buy a used i7-10700K at about $180 or a used 10900K at about $260, from a seller with returns. Test it on arrival.
2. Best value, if the used chip also fails or you want a warranty: an i5-12600K or i7-12700K plus a B760 DDR4 board. This is roughly $380 for the Micro Center bundle (12600KF) and more for a 12700K. It is the lowest long-term risk and the highest single-thread speed. 128 GB DDR4 compatibility needs checking before you buy.
3. Alternative: a 5800X3D plus a B550 board at about $280-340 for the chip, plus the board. It runs RimWorld well, but 4x32 GB at DDR4-3200 on AM4 is the weak spot.
Avoid: a new 10900K at $400-530; an 11900K or 11700K on this board (BIOS support not found); a DDR5 platform (about $1,700 or more for 128 GB); a 14600K; and used CPUs from sellers who do not accept returns.

Caveat: several search summaries conflicted with the sources, and ASUS's pages were only partly readable. Confirm the CPU list and BIOS notes in a browser before buying.
