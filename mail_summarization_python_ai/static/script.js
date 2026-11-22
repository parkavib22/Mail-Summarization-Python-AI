const form = document.getElementById("emailForm");
const result = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.textContent = "Fetching emails. Please wait...";

  const formData = {
    email: document.getElementById("email").value,
    password: document.getElementById("password").value
  };

  try {
    const response = await fetch("/fetch-emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    const data = await response.json();

    if (!response.ok) throw new Error(data.error || "Something went wrong.");

    result.replaceChildren();
    const heading = document.createElement("h2");
    heading.textContent = "Email Summary";
    const summary = document.createElement("p");
    summary.textContent = data.summary;
    const attachmentHeading = document.createElement("h3");
    attachmentHeading.textContent = `Attachments downloaded: ${data.attachment_count}`;
    result.append(heading, summary, attachmentHeading);

    if (data.attachments.length) {
      const list = document.createElement("ul");
      data.attachments.forEach((name) => {
        const item = document.createElement("li");
        item.textContent = name;
        list.appendChild(item);
      });
      result.appendChild(list);
    } else {
      const none = document.createElement("p");
      none.textContent = "No attachments were found in the fetched emails.";
      result.appendChild(none);
    }
  } catch (error) {
    result.textContent = error.message;
  }
});
