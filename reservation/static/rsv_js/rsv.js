$(function(){

  console.log(sessionStorage.getItem('auto_refresh')); 
  console.log(sessionStorage.getItem('date'));
  var date = sessionStorage.getItem('date');

  if (sessionStorage.getItem('auto_refresh')) { //対応する月のカレンダー表示のために遷移してきた場合

    var elements = document.getElementsByClassName("rs_" + date);
    $('.rsv_day').removeClass('table-danger active'); //カレンダーのマスの赤を削除 
    $('.active_event').addClass('event_hide');  //イベントカード全てを一旦非表示
    $('.active_event').removeClass('active_event'); //表示していたイベントカードを非表示(表示の'active_event'クラスを削除)
    $('.'+date).addClass("active_event"); //該当の日にちのイベントカードを表示
  
    for (var i = 0; i < elements.length; i++) {
      elements[i].classList.add("table-danger","active");
  
    }

  }
  sessionStorage.removeItem('auto_refresh'); //sessionStorageに保存したデータを削除
  sessionStorage.removeItem('date'); //sessionStorageに保存したデータを削除



  $('td').on('click',
  function(){
    // alert('クリックイベントが取得できていれば表示されます。');
    $('.rsv_day').removeClass('table-danger active');
    $('.active_event').addClass('event_hide');
    $('.active_event').removeClass('active_event');
    $(this).addClass('table-danger active');
    
    var active_date = $(this).find('.active').text()
    console.log(active_date);

    $('.'+active_date).addClass("active_event");


  },

  );

  
  $(window).scroll(function () {
    if($(window).scrollTop() > 20) {
      $('nav').addClass('sticky-top');
    } else {
      $('nav').removeClass('sticky-top');
    }
  });
});
// クリックした日付のクラス
  
function highlightDay(date, group_pk, month_current) { //グループのカレンダーでイベントの表示ボタンを押すとカレンダーの日付に色をつけ、イベント表示
  
  // クリックされた日付を年月日に分割する
  // 日付文字列の正規表現を定義する
  const dateRegex = /^(\d{4})年(\d{1,2})月(\d{1,2})日$/;
  const matches = date.match(dateRegex); // 正規表現で年、月、日を抽出
  const matches_current = month_current.match(dateRegex); // 正規表現で年、月を抽出(現在の年月)
  
  
  if (!matches) {
    console.error('Invalid date format:', date);
    return;
  }
  if (!matches_current) {
    console.error('Invalid date format:', month_current);
    return;
  }
  
  const year = parseInt(matches[1]); // 年を数値に変換して取得
  const month = parseInt(matches[2]); // 月を数値に変換して取得
  const day = parseInt(matches[3]); // 日を数値に変換して取得
  
  const year_now = parseInt(matches_current[1]); // 年を数値に変換して取得
  const month_now = parseInt(matches_current[2]); // 月を数値に変換して取得
  
  console.log(year,month,day);
  console.log(year_now, month_now);
  if (year==year_now && month==month_now){
    console.log("OK");
    var elements = document.getElementsByClassName("rs_" + date);
    $('.rsv_day').removeClass('table-danger active');
    $('.active_event').addClass('event_hide');
    $('.active_event').removeClass('active_event');
    $('.'+date).addClass("active_event");
    for (var i = 0; i < elements.length; i++) {
      elements[i].classList.add("table-danger","active");
  
    }
  }else{
    console.log("NG");
    // 新しいURLを作成する
    const urlInput = document.querySelector('#redirect-url');
    var url = urlInput.value  + year + "/" + month + "/";

    // console.log("*******");
    // console.log(urlInput.value);
    // console.log(url);

    sessionStorage.setItem('auto_refresh', true); //sessionStorageに画面遷移のフラグを保存
    sessionStorage.setItem('date', date); //sessionStorageにデータを保存

    window.location.href = url; //カレンダーの月を変えるため遷移

  }


}


