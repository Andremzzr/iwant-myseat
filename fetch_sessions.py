import os
from dotenv import load_dotenv
load_dotenv()

from curl_cffi import requests
from datetime import datetime, timedelta
import sys

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Aviso: Telegram não configurado (Faltam variáveis de ambiente).")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, impersonate="chrome110")
        response.raise_for_status()
        print("Notificação enviada com sucesso pro Telegram!")
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")
        if hasattr(response, 'text'):
            print(f"Detalhes do erro do Telegram: {response.text}")

LAST_AVAILABLE_DATE = datetime(2026,8,19)


def get_seats(url, qtd_seats):
    try:
        response = requests.get(url, impersonate="chrome110")
        response.raise_for_status()
        data = response.json()
        lines = data['lines']
        available_seats = ""
        for line in lines:
            seats = line['seats']
            bg = int(len(seats) * 0.3)
            end = int(len(seats) * 0.7)

            result = [obj for obj in seats[bg:end] if obj["status"] == 'Available' and obj["typeDescription"] != "Acompanhante"]
            if len(result) >= qtd_seats:
                available_seats += f"\n{len(result)} cadeiras livres na fila {line["line"]}"
        return available_seats
    except Exception as e:
        print(f"Erro ao acessar API: {e}")
        return False

def get_target_dates(current_date):
    """
    Retorna os dias 20, 21 e 22 de agosto se a data atual for menor ou igual a 19 de agosto.
    Caso contrário, retorna o dia atual e os 2 próximos dias.
    """
    if current_date.month == LAST_AVAILABLE_DATE.month and current_date.day <= LAST_AVAILABLE_DATE.day:
        return [
            datetime(current_date.year, 8, 20).strftime('%Y-%m-%d'),
            datetime(current_date.year, 8, 21).strftime('%Y-%m-%d'),
            datetime(current_date.year, 8, 22).strftime('%Y-%m-%d'),
        ]
    else:
        return [
            (current_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)
        ]

def main():
    if len(sys.argv) < 2:
        print("Uso: python fetch_sessions.py \"Título do Filme\"")
        print("Exemplo: python fetch_sessions.py \"A Odisseia\"")
        return

    title_to_search = sys.argv[1]
    qtd_seats = int(sys.argv[2]) or 1
    current_date = datetime.now()
    target_dates = get_target_dates(current_date)

    print(f"Procurando por sessões IMAX do filme: '{title_to_search}'")

    found_any_session = False
    message_lines = [f"<b>Novas sessões IMAX encontradas para {title_to_search}!</b>\n"]

    for date_str in target_dates:
        url = f"https://api-content.ingresso.com/v0/sessions/city/5/theater/1014/partnership/home/groupBy/sessionType?date={date_str}"
        print(f"\n--- Buscando dados para {date_str} ---")

        try:
            response = requests.get(url, impersonate="chrome110")
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Erro ao acessar API: {e}")
            continue

        if not data or not isinstance(data, list):
            print("Nenhum dado de sessão retornado.")
            continue

        day_data = data[0]
        returned_date = day_data.get("date")

        # Verifica se o date está correto. Se não houver sessão, ele redireciona para o dia anterior.
        if returned_date != date_str:
            print(f"Aviso: Não há sessões para {date_str}. A API retornou os dados do dia {returned_date}.")
            continue

        movies = day_data.get("movies", [])
        movie_found = next((m for m in movies if m.get("title") == title_to_search), None)

        if not movie_found:
            print(f"Filme '{title_to_search}' não encontrado nas sessões de hoje.")
            continue

        # Verifica no corpo do objeto do filme se há sessions em IMAX
        session_types = movie_found.get("sessionTypes", [])
        imax_sessions = [st for st in session_types if "IMAX" in st.get("type", [])]

        if not imax_sessions:
            print(f"O filme '{title_to_search}' está em cartaz, mas NÃO há sessões em IMAX.")
        else:
            print(f"Sessões IMAX encontradas:")
            message_lines.append(f"\n📅 <b>Data: {date_str}</b>")
            found_any_session = True
            for st in imax_sessions:
                # O 'type' normalmente vem como ["IMAX", "Legendado"] etc
                session_type_desc = " / ".join(st.get("type", []))
                for session in st.get("sessions", []):
                    time = session.get("time")
                    room = session.get("room")
                    price = session.get("price")
                    default_sector = session.get("defaultSector")
                    id = session.get("id")
                    seats_url = f"https://api.ingresso.com/v1/sessions/{id}/sections/{default_sector}/seats"
                    msg = f" - [{session_type_desc}] Horário: {time} | Sala: {room} | Preço: R${price:.2f} \n Link: https://checkout.ingresso.com/assentos?sessionId={id}&partnership=home"
                    print(msg)
                    seats = get_seats(seats_url, qtd_seats)
                    print(seats)
                    message_lines.append(msg)
                    message_lines.append(seats)

    if found_any_session:
        send_telegram_message("\n".join(message_lines))

if __name__ == "__main__":
    main()
