import csv
import os
from datetime import datetime
from time import sleep
from plyer import notification

# Nome do arquivo CSV que armazena os eventos
CSV_FILE = 'agenda.csv'

# Função para inicializar o arquivo CSV
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Data', 'Hora', 'Evento', 'Frequência', 'Dias da Semana'])

# Função para adicionar um evento
def add_event(data, hora, evento, frequencia='Uma vez', dias=''):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data, hora, evento, frequencia, dias])
    print(f"Evento adicionado: {evento} em {data} às {hora} com frequência: {frequencia} nos dias: {dias}")

# Função para listar todos os eventos
def list_events():
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Pular o cabeçalho
        events = list(reader)
        if events:
            print("Eventos agendados:")
            for event in events:
                print(f"Data: {event[0]}, Hora: {event[1]}, Evento: {event[2]}, Frequência: {event[3]}, Dias: {event[4]}")
        else:
            print("Nenhum evento encontrado.")

# Função para remover um evento específico
def remove_event(data, hora):
    updated_events = []
    removed = False
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if row[0] == data and row[1] == hora:
                removed = True
            else:
                updated_events.append(row)
    
    # Escrever os eventos atualizados de volta ao CSV
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(updated_events)

    if removed:
        print(f"Evento removido em {data} às {hora}")
    else:
        print(f"Nenhum evento encontrado em {data} às {hora}")

# Função para enviar notificação
def send_notification(evento, data, hora):
    notification.notify(
        title="Lembrete de Evento",
        message=f"Evento: {evento}\nData: {data}\nHora: {hora}",
        timeout=10  # Duração da notificação em segundos
    )

# Função para verificar se é hora do evento e enviar notificação
def check_events():
    while True:
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday()  # Usando weekday() para obter o dia da semana atual (0=segunda, ..., 6=domingo)
        
        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Pular o cabeçalho
            for row in reader:
                # Verifica se a linha tem o número correto de colunas
                if len(row) < 5:
                    continue  # Ignorar linhas com dados insuficientes

                event_date = row[0]
                event_time = row[1]
                event_name = row[2]
                frequency = row[3]
                weekdays = row[4].strip().split(',') if row[4] else []  # Converte os dias da semana em uma lista e remove espaços

                # Verificar se a data e a hora do evento coincidem com o horário atual
                if event_date == current_date and event_time == current_time and frequency.lower() == 'uma vez':
                    send_notification(event_name, event_date, event_time)
                    print("\n")
                    remove_event(event_date, event_time)  # Remover evento após notificação

                # Lógica para verificar eventos repetidos
                match frequency.lower():
                    case 'diariamente':
                        send_notification(event_name, current_date, event_time)
                        print("\n")
                    case 'semanalmente':
                        # Verifica se o dia atual está na lista de dias da semana (convertendo para inteiros)
                        if str(current_weekday) in [day.strip() for day in weekdays]:
                            send_notification(event_name, current_date, event_time)
                            print("\n")
                    case 'mensalmente':
                        # Verifica se é o primeiro dia do mês
                        if now.day == 1:  # Para verificar eventos no primeiro dia do mês
                            send_notification(event_name, current_date, event_time)
                            print("\n")
                    case 'anualmente':
                        # Verifica se é o primeiro dia do mês e se é o dia específico do evento
                        event_day, event_month = map(int, event_date.split('/')[0:2])
                        if now.day == event_day and now.month == event_month:
                            send_notification(event_name, current_date, event_time)
                            print("\n")

        sleep(60)  # Verifica os eventos a cada minuto

# Menu principal da agenda
def menu():
    while True:
        print("\n=== Agenda ===")
        print("1. Adicionar evento")
        print("2. Listar eventos")
        print("3. Remover evento")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            data = input("Digite a data (DD/MM/AAAA): ")
            hora = input("Digite a hora (HH:MM): ")
            evento = input("Descreva o evento: ")
            frequencia = input("Digite a frequência (Uma vez, Diariamente, Semanalmente, Mensalmente, Anualmente): ")
            dias = ''
            if frequencia.lower() == 'semanalmente':
                dias = input("Digite os dias da semana (separados por vírgula, ex: 0,1 para Segunda e Terça): ")
            add_event(data, hora, evento, frequencia, dias)
        elif opcao == '2':
            list_events()
        elif opcao == '3':
            data = input("Digite a data do evento a remover (DD/MM/AAAA): ")
            hora = input("Digite a hora do evento a remover (HH:MM): ")
            remove_event(data, hora)
        elif opcao == '4':
            print("Saindo da agenda.")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Executar o menu e inicializar o arquivo CSV ao rodar o script
if __name__ == "__main__":
    init_csv()
    # Executa o menu em paralelo com a checagem de eventos
    import threading
    t = threading.Thread(target=check_events)
    t.daemon = True
    t.start()
    
    menu()
