const API_URL = "http://127.0.0.1:5000/api";


const loginForm = document.getElementById("loginForm");


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;


            const button =
                document.getElementById("loginButton");

            const message =
                document.getElementById("loginMessage");


            button.disabled = true;

            button.textContent = "Logging in...";

            message.textContent = "";


            try {

                const response = await fetch(
                    `${API_URL}/auth/login`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            email: email,
                            password: password
                        })
                    }
                );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Login failed."
                    );

                }


                localStorage.setItem(
                    "access_token",
                    data.access_token
                );


                localStorage.setItem(
                    "user",
                    JSON.stringify(data.user)
                );


                message.className =
                    "message success";

                message.textContent =
                    "Login successful. Redirecting...";


                setTimeout(() => {

                    window.location.href =
                        "dashboard.html";

                }, 700);


            } catch (error) {

                message.className =
                    "message error";

                message.textContent =
                    error.message;

            }


            button.disabled = false;

            button.textContent = "Login";

        }
    );

}


const registerForm =
    document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const name =
                document.getElementById("name")
                .value.trim();

            const email =
                document.getElementById("email")
                .value.trim();

            const password =
                document.getElementById("password")
                .value;

            const confirmPassword =
                document.getElementById("confirmPassword")
                .value;


            const button =
                document.getElementById(
                    "registerButton"
                );

            const message =
                document.getElementById(
                    "registerMessage"
                );


            if (password !== confirmPassword) {

                message.className =
                    "message error";

                message.textContent =
                    "Passwords do not match.";

                return;

            }


            if (password.length < 6) {

                message.className =
                    "message error";

                message.textContent =
                    "Password must contain at least 6 characters.";

                return;

            }


            button.disabled = true;

            button.textContent =
                "Creating account...";

            message.textContent = "";


            try {

                const response = await fetch(
                    `${API_URL}/auth/register`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            name: name,
                            email: email,
                            password: password
                        })
                    }
                );


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Registration failed."
                    );

                }


                message.className =
                    "message success";

                message.textContent =
                    "Account created successfully. Redirecting to login...";


                setTimeout(() => {

                    window.location.href =
                        "index.html";

                }, 1000);


            } catch (error) {

                message.className =
                    "message error";

                message.textContent =
                    error.message;

            }


            button.disabled = false;

            button.textContent =
                "Create Account";

        }
    );

}