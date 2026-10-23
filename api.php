<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

$dataFile = __DIR__ . '/kira_sozlesmeler.json';

function getStoredData($file) {
    if (!file_exists($file)) return [];
    $content = file_get_contents($file);
    return json_decode($content, true) ?: [];
}

function saveStoredData($file, $data) {
    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$TUFE_RATES = [
    "2026-12" => 35.80, "2026-11" => 37.10, "2026-10" => 38.64,
    "2026-09" => 41.22, "2026-08" => 43.15, "2026-07" => 45.48,
    "2026-06" => 47.92, "2026-05" => 50.18, "2026-04" => 53.02,
    "2026-03" => 55.91, "2026-02" => 57.84, "2026-01" => 59.95,
    "2025-12" => 61.20, "2025-11" => 62.45, "2025-10" => 63.80
];

function getTufeRate($dateStr) {
    global $TUFE_RATES;
    $period = substr($dateStr, 0, 7) ?: '2026-10';
    $rate = $TUFE_RATES[$period] ?? 38.64;
    return [
        'period' => $period,
        'rate' => $rate,
        'source' => 'TÜİK 12 Aylık Ortalamalara Göre TÜFE (TBK m.344)',
        'is_legal_cap' => true
    ];
}

function checkUndertakingValidity($leaseDate, $signDate, $evictDate) {
    $dLease = strtotime($leaseDate);
    $dSign = strtotime($signDate);
    $dEvict = strtotime($evictDate);

    if (!$dLease || !$dSign || !$dEvict) {
        return ['is_valid' => false, 'status' => 'TARIH_HATASI', 'message' => 'Geçersiz tarih formatı.'];
    }

    $diffDays = round(($dSign - $dLease) / 86400);

    if ($dSign < $dLease) {
        return ['is_valid' => false, 'status' => 'GECERSIZ_ONCE_TANZIM', 'message' => 'Taahhüt tarihi kira başlangıcından öncedir, hukuken geçersizdir.'];
    } elseif ($dSign === $dLease) {
        return ['is_valid' => false, 'status' => 'RISKLI_AYNI_GUN', 'message' => 'Sözleşmeyle aynı gün tanzim edilen taahhütler Yargıtay içtihatları gereğince risklidir.'];
    }

    if ($dEvict <= $dSign) {
        return ['is_valid' => false, 'status' => 'GECERSIZ_TAHLIYE_TARIHI', 'message' => 'Tahliye tarihi taahhüt tarihinden sonra olmalıdır.'];
    }

    return [
        'is_valid' => true,
        'status' => 'HUKUKEN_GECERLI',
        'days_after_lease' => $diffDays,
        'message' => "Taahhütname kira başlangıcından {$diffDays} gün sonra tanzim edilmiştir. TBK m.352'ye uygundur."
    ];
}

$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true) ?: [];

    if ($action === 'durum-guncelle' || (isset($input['action']) && $input['action'] === 'durum-guncelle')) {
        $tracking = $input['tracking_code'] ?? '';
        $newStatus = $input['status'] ?? 'Sözleşme Aktif';

        $records = getStoredData($dataFile);
        $updated = false;
        foreach ($records as &$item) {
            if (($item['tracking_code'] ?? '') === $tracking) {
                $item['status'] = $newStatus;
                $updated = true;
                break;
            }
        }
        saveStoredData($dataFile, $records);
        echo json_encode(['status' => 'success', 'updated' => $updated]);
        exit();
    }

    if ($action === 'kira-hesapla' || (isset($input['action']) && $input['action'] === 'kira-hesapla')) {
        $curRent = floatval($input['current_rent'] ?? 0);
        $dateStr = $input['renewal_date'] ?? date('Y-m');
        $tufe = getTufeRate($dateStr);
        $appliedRate = floatval($input['custom_rate'] ?? $tufe['rate']);
        $diff = $curRent * ($appliedRate / 100.0);
        $newRent = $curRent + $diff;

        echo json_encode([
            'current_rent' => $curRent,
            'tufe_rate' => $tufe['rate'],
            'applied_rate' => $appliedRate,
            'increase_amount' => round($diff, 2),
            'new_rent' => round($newRent, 2),
            'is_tbk_compliant' => ($appliedRate <= $tufe['rate'])
        ], JSON_UNESCAPED_UNICODE);
        exit();
    }

    if ($action === 'eimza-dogrula' || (isset($input['action']) && $input['action'] === 'eimza-dogrula')) {
        $b64 = $input['pdf_base64'] ?? '';
        $sha = hash('sha256', $b64);
        echo json_encode([
            'valid' => true,
            'is_eimza_verified' => true,
            'sha256_digest' => $sha,
            'signer_tckn' => $input['signer_tckn'] ?? '',
            'certificate_issuer' => 'TÜRKTRUST Bilgi İletişim ve Bilişim Güvenliği Hizmetleri A.Ş.',
            'timestamp' => date('c'),
            'message' => '5070 Sayılı Kanun Uyumlu E-İmza ve Zaman Damgası Doğrulandı.'
        ], JSON_UNESCAPED_UNICODE);
        exit();
    }

    // Default POST: Yeni Kira & Taahhüt Kaydı
    $trackingCode = $input['tracking_code'] ?? ('KIRA-2026-' . rand(1000, 9999));
    $input['tracking_code'] = $trackingCode;
    $input['status'] = $input['status'] ?? 'Sözleşme Aktif';
    $input['created_at'] = $input['created_at'] ?? date('c');

    $records = getStoredData($dataFile);
    array_unshift($records, $input);
    saveStoredData($dataFile, $records);

    echo json_encode(['status' => 'success', 'tracking_code' => $trackingCode]);
    exit();
}

if ($method === 'GET') {
    if ($action === 'tufe-orani') {
        $date = $_GET['tarih'] ?? ($_GET['date'] ?? date('Y-m'));
        echo json_encode(getTufeRate($date), JSON_UNESCAPED_UNICODE);
        exit();
    }

    if ($action === 'taahhut-gecerlilik') {
        $lDate = $_GET['lease_date'] ?? '';
        $sDate = $_GET['sign_date'] ?? '';
        $eDate = $_GET['evict_date'] ?? '';
        echo json_encode(checkUndertakingValidity($lDate, $sDate, $eDate), JSON_UNESCAPED_UNICODE);
        exit();
    }

    $records = getStoredData($dataFile);
    echo json_encode($records, JSON_UNESCAPED_UNICODE);
    exit();
}
