setTimeout(() => {
    const alert = document.querySelector('div[role="alert"]');
    if(alert){
       
      alert.style.opacity = '0';
       
      setTimeout(() => alert.remove(), 1000);
    }
  }, 3000); 