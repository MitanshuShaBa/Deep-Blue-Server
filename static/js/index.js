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
let h3Instruction = document.getElementById("instruction");
const NUM_OF_IMAGES = 10

let files = [];

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      streamingDocument.srcObject = stream;
      startCapture();
    })
    .catch(function (error) {
      console.log("Something went wrong!", error);
    });
}

const startCapture = () => {
  h3Instruction.innerHTML = "Place your face in the frame";
  console.log("startCapture called");
  setTimeout(() => {
    let i = 3
  let timer = setInterval(() => {
      h3Instruction.innerHTML = `Pictures will start being taken in ${i}`
      i--;
      if (i==-1){
        clearInterval(timer)

        // Take pictures
        h3Instruction.innerHTML = ""
        let j = 0
        let pictureTimer = setInterval(() => {
          capture()
          console.log("Taking Picture", j+1)
          j++
          if (j==NUM_OF_IMAGES){
            clearInterval(pictureTimer)
            h3Instruction.innerHTML = "Pictures are taken you can fill the information below now"
          }
        }, 1000);
      }
  }, 1000);
  }, 3000);
  
};

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
