document.querySelectorAll('.route-container').forEach(container => {
  const clicavel = container.querySelector('.route-content');
  const botoes = container.querySelector('.botao-duplo');

  clicavel.addEventListener('click', () => {
    botoes.classList.toggle('mostrar'); // ativa/desativa os botões
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const botaoAdicionar = document.getElementById('adicionar-wrapper');
  const formWrapper = document.getElementById('form-favorito-wrapper');
  const botaoFechar = document.getElementById('btn-fechar');

  if (botaoAdicionar && formWrapper && botaoFechar) {
    botaoAdicionar.addEventListener('click', () => {
      botaoAdicionar.style.display = 'none';
      formWrapper.style.display = 'flex'; // ou 'block', depende do layout
    });

    botaoFechar.addEventListener('click', () => {
      formWrapper.style.display = 'none';
      botaoAdicionar.style.display = 'flex'; // mostra o botão novamente
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-favorito');
  const nomeInput = document.getElementById('nome');
  const enderecoInput = document.getElementById('endereco');
  const favoritosLista = document.getElementById('favoritos-lista');
  const btnFechar = document.getElementById('btn-fechar');
  const adicionarWrapper = document.getElementById('adicionar-wrapper');
  const formWrapper = document.getElementById('form-favorito-wrapper');
  const btnAdicionar = document.getElementById('btn-adicionar');

  function criarFavorito(nome, endereco) {
    const novoFavorito = document.createElement('div');
    novoFavorito.className = 'route-container';
    novoFavorito.innerHTML = `
      <div class="route-header">
        <div class="route-content">
          <div class="icon-border">
            <svg id="favoritos" width="31" height="31" viewBox="0 0 31 31" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12.3262 6.53731C13.5301 3.53602 14.132 2.03537 15.11 1.82739C15.3671 1.77271 15.6329 1.77271 15.89 1.82739C16.868 2.03537 17.4699 3.53602 18.6738 6.5373C19.3585 8.24408 19.7008 9.09747 20.3413 9.67791C20.521 9.84071 20.716 9.98571 20.9236 10.1109C21.6639 10.5571 22.5881 10.6398 24.4365 10.8054C27.5654 11.0856 29.1299 11.2257 29.6076 12.1177C29.7066 12.3025 29.7738 12.5025 29.8066 12.7095C29.965 13.7089 28.8149 14.7553 26.5147 16.848L25.8759 17.4291C24.8005 18.4075 24.2628 18.8967 23.9518 19.5072C23.7652 19.8734 23.6402 20.2678 23.5815 20.6746C23.4838 21.3528 23.6413 22.0625 23.9562 23.4818L24.0687 23.9889C24.6335 26.5343 24.9158 27.807 24.5633 28.4326C24.2467 28.9945 23.6635 29.3542 23.0193 29.385C22.302 29.4193 21.2914 28.5958 19.2702 26.9488C17.9386 25.8637 17.2728 25.3211 16.5336 25.1092C15.8582 24.9155 15.1419 24.9155 14.4664 25.1092C13.7272 25.3211 13.0614 25.8637 11.7298 26.9488C9.70858 28.5958 8.69798 29.4193 7.98075 29.385C7.3365 29.3542 6.75329 28.9945 6.43667 28.4326C6.08418 27.807 6.36655 26.5343 6.93129 23.989L7.04381 23.4818C7.35872 22.0625 7.51618 21.3528 7.41846 20.6746C7.35985 20.2678 7.23476 19.8734 7.04819 19.5072C6.73718 18.8967 6.19948 18.4075 5.12409 17.4291L4.48533 16.848C2.1851 14.7553 1.03498 13.7089 1.19337 12.7095C1.22617 12.5025 1.29345 12.3025 1.39239 12.1177C1.87014 11.2257 3.43461 11.0856 6.56353 10.8054C8.41188 10.6398 9.33605 10.5571 10.0764 10.1109C10.284 9.98571 10.4791 9.84071 10.6587 9.67791C11.2992 9.09747 11.6415 8.24408 12.3262 6.53731Z" fill="#222222" stroke="#222222" stroke-width="2" />
            </svg>
          </div>
          <div class="route-info">
            <div>
              <p class="form-title">${nome}</p>
              <p class="endereco">${endereco}</p>
            </div>
          </div>
        </div>
        <div>
          <button class="menu-button">
            <img width="36" height="36" src="../static/images/tres-pontos.png" alt="">
          </button>
        </div>
      </div>
      <div class="botao-duplo">
        <button class="botao origem">Origem</button>
        <button class="botao destino">Destino</button>
      </div>
    `;

    favoritosLista.appendChild(novoFavorito);

    const content = novoFavorito.querySelector('.route-content');
    const botoes = novoFavorito.querySelector('.botao-duplo');

    content.addEventListener('click', () => {
      botoes.classList.toggle('mostrar');
    });
  }

  // Adiciona novo favorito no submit
  form.addEventListener('submit', function (event) {
    event.preventDefault(); // impede recarregamento

    const nome = nomeInput.value.trim();
    const endereco = enderecoInput.value.trim();

    if (nome && endereco) {
      criarFavorito(nome, endereco);
      form.reset();

      // Esconde formulário e mostra botão de adicionar
      formWrapper.style.display = 'none';
      adicionarWrapper.style.display = 'flex';
    }
  });

  // Mostra formulário
  btnAdicionar.addEventListener('click', () => {
    formWrapper.style.display = 'flex';
    adicionarWrapper.style.display = 'none';
  });

  // Fecha formulário
  btnFechar.addEventListener('click', () => {
    formWrapper.style.display = 'none';
    adicionarWrapper.style.display = 'flex';
  });
});

