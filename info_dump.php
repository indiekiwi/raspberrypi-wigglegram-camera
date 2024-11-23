<?php

echo "\n===== Connected cameras =====\n";
exec('v4l2-ctl --list-devices | grep -i -A 1 "CAM"', $output);
echo implode("\n", $output) . "\n\n";

echo "\n===== Image sets with delay details =====\n";
exec("ls -lh --time-style=full-iso images/", $output);
$data = [];
foreach ($output as $line) {
	if (preg_match('@\d{2}\:\d{2}\:\d{2}\.(\d{3})\d{6} \+\d+ (\d{4}(\d{6}))_(\w).jpg@', $line, $m)) {
		$data[$m[2]][$m[4]] = (int) ($m[3] . $m[1]);
	}
}

foreach ($data as $setKey => $set) {
	asort($set);
	$prev = null;
	$first = true;
	$totalDelay = 0;
	$line = ["[$setKey:%dms]"];
	foreach ($set as $setIndex => $time) {
		$delay = $prev == 0 ? 0 : $time - $prev;
		$prev = $time;
                $totalDelay += $delay;
		$line[] = "$setIndex +{$delay}ms";
		$first = false;
	}
	$line[0] = sprintf($line[0], $totalDelay);
	echo implode(', ', $line) . PHP_EOL;
}
echo "\n";
