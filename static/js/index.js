let streamingDocument = document.getElementById("streaming");
let nameDiv = document.getElementById("name");
let dobDiv = document.getElementById("dob");
let emailDiv = document.getElementById("email");
let genderDiv = document.getElementById("gender");
let phoneNumDiv = document.getElementById("phone_num");
let addressDiv = document.getElementById("address");
let tempDiv = document.getElementById("temp");
let maskDiv = document.getElementById("mask");
let purposeDiv = document.getElementById("purpose");

let files = [];

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      streamingDocument.srcObject = stream;
    })
    .catch(function (error) {
      console.log("Something went wrong!", error);
    });
}

function capture() {
  var canvas = document.getElementById("canvas");
  var video = document.getElementById("streaming");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas
    .getContext("2d")
    .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
  canvas.toBlob((blob) => {
    const file = new File([blob], "name");
    files.push(file);
  });
}

fetch("/log")
  .then((response) => {
    return response.json();
  })
  .then((data) => {
    tempDiv.value = data.temp;
    maskDiv.value = data.mask;
  })
  .catch((err) => console.log(err));

const logEntry = () => {
  const user_data = {
    address: addressDiv.value,
    dob: dobDiv.value,
    email: emailDiv.value,
    gender: genderDiv.value,
    name: nameDiv.value,
    phone_number: phoneNumDiv.value,
    photo_url: "",
    role: "visitor",
  };

  let visit_log_data = {
    temp: tempDiv.value,
    mask: maskDiv.value,
    purpose: purposeDiv.value,
    type: "entry",
  };

  const formData = new FormData();
  formData.append("user_data", JSON.stringify(user_data));
  for (let i = 0; i < files.length; i++) {
    formData.append("photos", files[i]);
  }

  fetch("/create_user", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      return response.json();
    })
    .then(({ id, error }) => {
      if (error) {
        alert(error);
        return;
      }

      // We now have a user_id
      visit_log_data["user_id"] = id;

      fetch("/visit_log", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(visit_log_data),
      })
        .then((response) => {
          return response.json();
        })
        .then((data) => {
          console.log(data);

          // fetch("/reset")
          //   .then((response) => response.text())
          //   .then((data) => console.log(data));
        })
        .catch((err) => console.log("error", err));
    });
};
