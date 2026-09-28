/*
    The code of this file is for the mobile view of the web pages.
    
    The code was written by the author (Student No.: 200212427 of the University of London) of the project, and was used on the website <howa.space> that was written and owned by the same author.
*/
// store the state of the view
let is_mobile = false;
let is_menu_open = false;

try{
    const menu_button = document.getElementById("menu_button");

    // check the screen width and change the mode between desktop and mobile
    const browser_resizing = () => {
        // mobile view is enabled for the screen width lower than 800 pixels
        is_mobile = window.innerWidth < 800 ? true : false;
        // update mobile menu  
        mobile_menu_update(is_mobile, is_menu_open);
    };

    // check the screen width if either the web pages are being loaded or resized or both
    window.addEventListener("load", browser_resizing);
    window.addEventListener("resize", browser_resizing);

    // change the menu layout for desktop and mobile view
    // input:
    // 1. is_mobile: boolean, true for mobile view, false otherwise
    // 2. is_menu_open: boolean, true when the menu is open, false otherwise
    const mobile_menu_update = (is_mobile, is_menu_open) => {
        // update the mobile menu
        const a_in_menu = document.querySelectorAll("#menu a");
        const div_a_in_menu = document.querySelectorAll("#menu div a");
        const div_in_menu = document.querySelectorAll("#menu div");
        const menu = document.getElementById("menu");
        // change the style of the menu according to the states of the menu and the view mode
        if (is_menu_open && is_mobile)
        {
            menu.style.display = "block";
            for (const a of a_in_menu) a.style.display = "block";
            for (const div_a of div_a_in_menu) div_a.style.display = "block";
            for (const div of div_in_menu)
            {
                div.style.display = "block";
                div.style.float = "right";
            }
            menu.style.padding = "0 0 1rem 0";
        }
        else if (!is_mobile)
        {
            menu.style.display = "inline";
            for (const a of a_in_menu) a.style.display = "inline";
            for (const div_a of div_a_in_menu) div_a.style.display = "inline";
            for (const div of div_in_menu)
            {
                div.style.display = "inline";
                div.style.float = "right";
            }
        }
        else
        {
            menu.style.display = "none";
        }

        // update the menu and menu button
        menu_button.style.display = is_mobile ? "block" : "none";
    };

    // update the menu state when user clicks the menu button
    menu_button.addEventListener('mouseup', () => {
        is_menu_open = !is_menu_open;
        mobile_menu_update(is_mobile, is_menu_open);
    });
} catch (error) {
    console.error('Error:', error);
}
