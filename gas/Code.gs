// ==========================================
// Google Apps Script (Web App) 側の実装例
// ==========================================

// 環境変数 (デプロイ時にスクリプトプロパティで設定することも推奨)
const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE'; // スプレッドシートのID
const EXPECTED_API_KEY = 'YOUR_SECRET_API_KEY_HERE'; // .env の GAS_API_KEY と一致させる

function doPost(e) {
  try {
    // 1. JSONペイロードのパース
    const jsonString = e.postData.contents;
    const data = JSON.parse(jsonString);
    
    // 【重要】GASの制約事項
    // GASのWeb App(doPost)は、仕様上カスタムリクエストヘッダー(X-API-KEY等)を直接取得できません。
    // 仕様書の「リクエストヘッダーに特定の X-API-KEY が含まれているかチェック」を厳密に実装する場合、
    // API Gatewayなどを経由する必要があります。
    // 代替案として、リクエストボディ(JSON)の内部にキーを含めるか、URLパラメータ(e.parameter.api_key)を使用します。
    // 
    // 今回は安全のため、Python側から送信されたペイロードにAPIキーを含める形に変更するか、
    // 簡易的にこのブロックでURLパラメータのチェック等を行うことをお勧めします。
    // 例(URLパラメータの場合): /exec?api_key=YOUR_SECRET_API_KEY_HERE
    // if (e.parameter.api_key !== EXPECTED_API_KEY) {
    //   return ContentService.createTextOutput(JSON.stringify({error: "Unauthorized"})).setMimeType(ContentService.MimeType.JSON);
    // }
    
    // 2. スプレッドシートへ書き込み
    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getActiveSheet();
    
    // データが配列の場合と単一オブジェクトの場合の両方に対応
    const dataArray = Array.isArray(data) ? data : (data.meals ? data.meals : [data]);
    
    // A: 摂取日時, B: メニュー, C: カロリー, D: タンパク質, E: 脂質, F: 炭水化物
    dataArray.forEach(item => {
      sheet.appendRow([
        item.eaten_at,
        item.menu,
        item.calories,
        item.protein,
        item.fat,
        item.carb
      ]);
    });
    
    return ContentService.createTextOutput(JSON.stringify({ status: "success", count: dataArray.length }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
