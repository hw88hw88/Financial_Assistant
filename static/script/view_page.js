/*
  document.getElementById("smallA").onclick = function () {
  changeSize("small");
  };
  document.getElementById("mediumA").onclick = function () {
    changeSize("medium");
  };
  document.getElementById("largeA").onclick = function () {
    changeSize("large");
  };
  function changeSize(c) {
    document.getElementsByTagName("body")[0].className = c;
  }

    Title: 7.3.5 What can we do with these elements when we have them, the lecture video of week 14 of CM1040 Web Development
    Author: The writer of the CM1040 module
    Date: 23 January 2022
    Code version: N/A
    Availability: the Coursera learning platform (https://www.coursera.org/learn/uol-web-development/lecture/SJumr/7-3-5-what-can-we-do-with-these-elements-when-we-have-them)

    The code below was adapted from the code in the lecture video of week 14 of CM1040 Web Development
*/

// make the 3As on top of the page clickable and
// change the text size
try{
  document.getElementById("smallA").onclick = function () {
    changeSize("smallFont");
  };
  document.getElementById("mediumA").onclick = function () {
    changeSize("mediumFont");
  };
  document.getElementById("largeA").onclick = function () {
    changeSize("largeFont");
  };
  function changeSize(size) {
    document.getElementsByTagName("body")[0].className = size;
  }
} catch (error) {
    console.error('Error:', error);
}


// Scroll Bar
/*

  // When the user scrolls the page, execute myFunction
  window.onscroll = function() {myFunction()};

  function myFunction() {
    var winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    var scrolled = (winScroll / height) * 100;
    document.getElementById("myBar").style.width = scrolled + "%";
  }

The following part of code was adapted from the W3schools tutorials

Title: How TO - Scroll Indicator
Author: Refsnes Data
Date: 28 September 2026
Code version: N/A
Availability: https://www.w3schools.com/howto/howto_js_scroll_indicator.asp

*/
try{
  const bar = document.getElementById("scrollBar");

  window.addEventListener("scroll", function () {
    const winScroll =
      document.body.scrollTop || document.documentElement.scrollTop;
    const height =
      document.documentElement.scrollHeight -
      document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    bar.style.width = scrolled + "%";
  });
} catch (error) {
    console.error('Error:', error);
}

