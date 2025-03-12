document.addEventListener("DOMContentLoaded", function () {
  // save document when saveBtn is clicked
  document.getElementById("saveBtn").addEventListener("click", function () {
    const documentId = window.location.pathname.split("/").pop();
    const documentText = quill.root.innerHTML;

    fetch("/save_document", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: documentId,
        document_text: documentText,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Document saved successfully!");
        } else {
          alert("Error saving document.");
        }
      })
      .catch((error) => alert("Network error."));
  });

  // handling folder clicks
  const folderItems = document.querySelector(".folder-btn");
  folderItems.array.forEach((element) => {
    element.addEventListener("click", function () {
      const folderId = this.getAttribute("data-folder-id");
      fetch(`/get_folder/$`);
    });
  });
});
