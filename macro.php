function get_accession_number($resource_filename)

{

	$filename = $resource_filename;
	$pattern = '/bampfa_([a-zA-Z0-9-]+)_.+/';
	preg_match($pattern, $filename, $matches);
	$captured_accession_number = $matches[1];
	$pattern = '/-/i';
	$temp = preg_replace($pattern, '.', $captured_accession_number);
	$pattern = '/([a-z]).([a-z])/i';
	$accession_number = preg_replace($pattern, '$1-$2', $temp);

	return $accession_number;

}
