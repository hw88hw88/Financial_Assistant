// The code of this file is for the chatting on the web page
// The code was written by the author (Student No.: 200212427 of the University of London) of the project, and was used on the website <howa.space> that was written and owned by the same author few years ago.

const query = document.getElementById('query');
const response = document.getElementById('response');
const enter_button = document.getElementById('enter');
const clear_button = document.getElementById('clear');
const server_msg = document.getElementById('server_msg');

// the sender ID or user ID
let sender = null;
// store the pending jobs
// The content format: jobs = [{id: 1, timer: timer_object}, {id: 2, timer: timer_object}]
const jobs = [];

try {
    // stop the timer that makes requests to the server
    const stop_timer = (timer) => {
        clearInterval(timer);
    };

    // make GET request to the web server to get the latest status of a job
    // input:
    // 1. job_id: the job ID of the job
    // output:
    // 1. return the completed job to the web page; or
    // 2. return the waiting message from the server to the web page
    const update_status = async (job_id) => {
        try{
            const url = window.location.href + 'status?job_id=' + job_id;
            const result_msg = await fetch(url);
            const result_json = await result_msg.json();

            if (result_json.status == 'pending')
            {
                // return the waiting message from the server to the web page
                sender = result_json.sender;
                server_msg.innerHTML = "<p>" + result_json.text + "</p>";
            }
            else if (result_json.status == 'completed')
            {
                // create a new p tag with the result of the completed job
                const message_element = document.createElement('p');
                message_element.innerHTML = "<b>Financial Assistant</b>:<br>" + result_json.text + "<br>";
                message_element.className = "response";
                message_element.style.width = "100%";
                message_element.style.padding = "1rem";
                message_element.style.borderWidth = "3px";
                message_element.style.borderStyle = "solid";
                message_element.style.borderColor = "#bc4749";
                message_element.style.borderRadius = "1rem";
                message_element.style.backgroundColor = "white";
                response.appendChild(message_element);
                // update the web page
                sender = result_json.sender;
                server_msg.innerHTML = "";
                // stop the timer and stop updating the status of the job
                for (const j in jobs)
                {
                    if (jobs[j].id == job_id){
                        stop_timer(jobs[j].timer);
                        jobs.splice(j, 1)
                    }
                }
            }
            else
            {
                // show the error message on the web page
                server_msg.innerHTML = `<p>Connection failed.<br>Please input new prompt or refresh the page.</p>`;
                // stop the timer and stop updating the status of the job
                for (const j in jobs)
                {
                    if (jobs[j].id == job_id){
                        stop_timer(jobs[j].timer);
                        jobs.splice(j, 1)
                    }
                }
            }
        }
        catch (ex)
        {
            // show error on the console
            console.error("Name (update_status): " + ex.name);
            console.error("Message: " + ex.message);
            // show the error message on the web page
            server_msg.innerHTML = `<p>Connection failed.<br>Please input new prompt or refresh the page.</p>`;
            // stop the timer and stop updating the status of the job
            for (const j in jobs)
            {
                if (jobs[j].id == job_id){
                    stop_timer(jobs[j].timer);
                    jobs.splice(j, 1)
                }
            }
        }
    };
    
    // show the prompt from the user in the dialogue, clear the input box, and create a new request
    // input: no input parameter
    // data needed: the content in the input box on the web page
    const user_enter = () => {
        let user_input = query.value;
        const message_element = document.createElement('p');
        message_element.innerHTML = "<b>You</b>:<br>" + user_input + "<br>";
        message_element.className = "query";
        message_element.style.padding = "1rem";
        message_element.style.width = "100%";
        message_element.style.textAlign = "right";
        message_element.style.borderWidth = "3px";
        message_element.style.borderStyle = "solid";
        message_element.style.borderColor = "#6a994e";
        message_element.style.borderRadius = "1rem";
        message_element.style.backgroundColor = "white";
        response.appendChild(message_element);
        // clear the user input box
        query.value = "";

        const api_chatbot = async () => {
            try{
                const result_msg = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: 
                        JSON.stringify(
                            {
                                'sender': sender,
                                'message': user_input
                            }
                        )                
                });
                const result_json = await result_msg.json();

                if (result_json.status == 'pending')
                {
                    sender = result_json.sender;
                    server_msg.innerHTML = "<p>" + result_json.text + " </p>";
                    const my_timer = setInterval(() => update_status(result_json.job_id), 3000);
                    jobs.push(
                        {
                            id: result_json.job_id, 
                            timer: my_timer
                        }
                    );
                }
                // if result_json.status != 'pending', it must be 'failed'.
                else if(result_json.sender)
                {
                    sender = result_json.sender;
                    server_msg.innerHTML = "<p>" + toString(result_json.text) + "<br>You can refresh the page to start a session later.</p>";
                }
                else
                {
                    server_msg.innerHTML = "<p>" + toString(result_json.text) + "<br>You can refresh the page to start a session later.</p>";
                }
            }
            catch (ex)
            {
                console.error("Name (api_chatbot): " + ex.name);
                console.error("Message: " + ex.message);
                server_msg.innerHTML = `<p>Connection failed.<br>Please refresh the page.</p>`;
            }
        };

        api_chatbot();
    };

    // call the user_enter() when user clicks 'enter' button on the web page
    enter_button.addEventListener('mouseup', () => {
        user_enter();
    });

    
    // call the user_enter() when user clicks 'enter' on the keyboard
    window.addEventListener("keyup", (event) => {
        if(event.key == "Enter") {
            if (!event.shiftKey)
                user_enter();
        }
    });

    // clear the input box when user clicks the 'clear' button on the web page
    clear_button.addEventListener('mouseup', () => {
        query.value = "";
    });

} catch (error) {
    console.error('Error:', error);
}
