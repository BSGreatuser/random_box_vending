import discord, uuid, asyncio, random, sqlite3, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption

ID = ''
PW = ''

####### 봇 초대 차단 필수 #######
token = ''
chargelogchannel = 
buylogchannel = 

client = discord.Client()
DiscordComponents(client)
db = sqlite3.connect('main.sqlite')
cursor = db.cursor()


@client.event
async def on_connect():
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS main(
                user TEXT,
                user_id TEXT,
                money TEXT,
                wrong_pin TEXT
                )
            ''')
    if not os.path.isfile('name.txt'):
        f = open('name.txt', 'w')
        f.close()
        f = open('price.txt', 'w')
        f.write('10000')
        f.close()
        os.mkdir('counting')
    print(client.user)


@client.event
async def on_message(message):
    if message.content == '!명령어':
        if not message.author.guild_permissions.administrator:
            return

        e = discord.Embed(description='', colour=discord.Colour.gold())
        e.add_field(name='!생성 <할 말>', value='버튼선택 메시지를 생성합니다', inline=False)
        e.add_field(name='!강제충전 @유저 <액수>', value='금액을 강제충전합니다', inline=False)
        e.add_field(name='!아이템추가 <상품명>', value='아이템을 추가합니다', inline=False)
        e.add_field(name='!아이템삭제 <상품명>', value='아이템을 삭제합니다', inline=False)
        e.add_field(name='!가격수정 <액수>', value='가격을 수정합니다', inline=False)
        e.add_field(name='!확률수정 <상품명>', value='확률을 수정합니다', inline=False)
        await message.reply(embed=e)

    if message.content.startswith('!생성'):
        if not message.author.guild_permissions.administrator:
            return
        try:
            await message.channel.send(message.content[4:], components=[
                [Button(style=ButtonStyle.red, label="구매", custom_id='buy'),
                 Button(style=ButtonStyle.green, label="충전", custom_id='charge'),
                 Button(style=ButtonStyle.green, label="정보", custom_id='info')
                 ]])
        except:
            await message.reply('할 말이 작성되지 않았습니다')
            return
        await message.delete()

    if message.content.startswith('!확률수정'):
        if not message.author.guild_permissions.administrator:
            return

        name = message.content[6:]

        if name == '':
            await message.reply('상품명이 작성되지 않았습니다')
            return

        with open('name.txt', 'r', encoding='UTF8') as f:
            read = str(f.read())

        if not name in read:
            await message.reply('존재하지 않는 상품입니다')
            return

        i = await message.reply('```확률을 입력해주세요```')

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            msg = await client.wait_for("message", timeout=20, check=check)
        except:
            await i.delete()
            await message.reply('시간이 초과되었습니다')
            return

        num = msg.content.split('%')[0]
        if not msg.content.endswith('%'):
            await msg.delete()
            await i.delete()
            await message.reply('%를 붙혀주세요')
            return

        if not str(num).isdecimal():
            await msg.delete()
            await i.delete()
            await message.reply('잘못된 확률입니다')
            return

        with open('name.txt', 'r', encoding='UTF8') as f:
            lines = f.readlines()

        for line in lines:
            if name in line:
                target = line
                n = lines.index(target)

                gjper = str(target).split(';')[1]
                change = str(target).replace(gjper, msg.content)

                lines[n] = change + '\n'
                with open('name.txt', 'w', encoding='UTF8') as f:
                    f.write(''.join(lines))

                await i.delete()
                await msg.delete()

                await message.reply(f'`{name}`의 확률이 수정 되었습니다\n{gjper.rstrip()} → {msg.content}')
                return

    if message.content.startswith('!가격수정'):
        if not message.author.guild_permissions.administrator:
            return

        try:
            amount = message.content.split(' ')[1]
        except IndexError:
            await message.reply('액수를 입력하지 않았습니다')
            return

        if not str(amount).isdecimal():
            await message.reply('올바르지 않은 액수입니다')
            return

        with open('price.txt', 'w') as f:
            f.write(amount)

        await message.reply('변경되었습니다')

    if message.content.startswith('!아이템삭제'):
        if not message.author.guild_permissions.administrator:
            return

        name = message.content[7:]

        if name == '':
            await message.reply('상품명이 작성되지 않았습니다')
            return

        with open('name.txt', 'r', encoding='UTF8') as f:
            lines = f.readlines()

        for line in lines:
            if name in line:
                target = line

                try:
                    lines.remove(target)
                except:
                    await message.reply('존재하지 않는 상품입니다')
                    return

                with open('name.txt', 'w', encoding='UTF8') as f:
                    f.write(''.join(lines))

                await message.reply(f'`{name}`이(가) 삭제되었습니다')
                return

    if message.content.startswith('!아이템추가'):
        if not message.author.guild_permissions.administrator:
            return

        name = message.content[7:]

        with open('name.txt', 'r', encoding='UTF8') as f:
            read = str(f.read())

        if name in read:
            await message.reply('이미 존재하는 상품입니다')
            return

        i = await message.reply('```확률을 입력해주세요```')

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        try:
            msg = await client.wait_for("message", timeout=20, check=check)
        except:
            await i.delete()
            await message.reply('시간이 초과되었습니다')
            return
        
        if not msg.content.endswith('%'):
            await msg.delete()
            await i.delete()
            await message.reply('%를 붙혀주세요')
            return
        
        if not str(msg.content).split('%')[0].isdecimal():
            await msg.delete()
            await i.delete()
            await message.reply('올바르지 않은 확률입니다')
            return
        
        added_name = name + ';' + msg.content

        with open('name.txt', 'a', encoding='UTF8') as f:
            f.write(added_name + '\n')

        await msg.delete()
        await i.delete()

        await message.reply(f'이름: `{name}`\n당첨확률: `{msg.content}`\n추가되었습니다')

    if message.content.startswith('!강제충전'):
        if message.author.guild_permissions.administrator:
            try:
                author = message.mentions[0]
                author_id = author.id
            except IndexError:
                await message.channel.send('유저가 지정되지 않았습니다')
                return

            j = message.content.split(" ")
            try:
                money = j[2]
            except IndexError:
                await message.channel.send('지급할 코인이 지정되지 않았습니다')
                return

            if not money.isdecimal():
                await message.channel.send('올바른 액수를 입력해주세요')
                return

            cursor.execute('SELECT money FROM main WHERE user_id = {0}'.format(author_id))
            result = cursor.fetchone()

            if result is None:
                with open(f'counting/{author_id}.txt', 'w') as f:
                    f.write('0')
                sql = 'INSERT INTO main(user, user_id, money, wrong_pin) VALUES(?,?,?,?)'
                val = (str(author), str(author_id), str(money), str('0'))

                embed1 = discord.Embed(colour=discord.Colour.green())
                embed1.add_field(name='✅  강제충전 성공', value='{0}님에게 `{1}`코인을 충전하였습니다'.format(author, money), inline=False)
                embed1.add_field(name='{0}님의 잔액'.format(author), value=str(money) + '코인', inline=False)
                await message.channel.send(embed=embed1)

                embed2 = discord.Embed(colour=discord.Colour.green())
                embed2.add_field(name='✅  강제충전', value='`{0}`코인이 강제충전 되었습니다'.format(money),
                                 inline=False)
                embed2.add_field(name='잔액', value=str(money) + '코인', inline=False)
                embed2.set_footer(text='유저정보가 없어 강제가입 되었습니다')
                await author.send(embed=embed2)
            else:
                sql = 'UPDATE main SET money = ? WHERE user_id = {0}'.format(author_id)
                result = str(result)
                n_money = result.replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                pls_money = int(n_money) + int(money)
                val = (str(pls_money),)

                embed1 = discord.Embed(colour=discord.Colour.green())
                embed1.add_field(name='✅  강제충전 성공', value='{0}님에게 `{1}`코인을 충전하였습니다'.format(author, money), inline=False)
                embed1.add_field(name='{0}님의 잔액'.format(author), value=str(pls_money) + '코인', inline=False)
                await message.channel.send(embed=embed1)

                embed2 = discord.Embed(colour=discord.Colour.green())
                embed2.add_field(name='✅  강제충전',
                                 value='{0}님에 의해 `{1}`코인이 강제충전 되었습니다'.format(message.author.name, money),
                                 inline=False)
                embed2.add_field(name='잔액', value=str(pls_money) + '코인', inline=False)
                await author.send(embed=embed2)

            cursor.execute(sql, val)
            db.commit()
            print(f"{author}에게 {money}코인이 강제충전됨")

    if message.content.startswith('!충전'):
        overwrite = message.channel.overwrites_for(message.author)
        if overwrite.manage_webhooks:
            j = message.content.split(" ")
            pin = message.content.split('-')
            try:
                allpin = j[1]
            except IndexError:
                embed = discord.Embed(title='❌  오류', description='핀번호를 입력해주세요', colour=0xFF0000)
                await message.channel.send(embed=embed)
                return

            if message.content[4:8].isdecimal() and message.content[9:13].isdecimal() \
                    and message.content[14:18].isdecimal() and message.content[19:23].isdecimal() \
                    and '-' in message.content[8:9] and '-' in message.content[13:14] and '-' in message.content[
                                                                                                 18:19] \
                    and len(message.content) < 26:
                if not len(pin[3]) == 6:
                    if len(pin[3]) == 4:
                        pass
                    else:
                        embed = discord.Embed(title='❌  오류', description='올바른 형식의 번호를 입력해주세요', colour=0xFF0000)
                        await message.channel.send(embed=embed)
                        return
                embed = discord.Embed(description="")
                embed.set_author(name='잠시만 기다려주세요',
                                 icon_url='https://cdn.discordapp.com/attachments/761785019726823445/780764667219542066/Rolling-1s-200px.gif')
                load = await message.channel.send(embed=embed)
                try:
                    options = ChromeOptions()
                    options.add_argument('headless')
                    options.add_argument("disable-gpu")
                    options.add_argument("disable-infobars")
                    options.add_argument("--disable-extensions")
                    options.add_argument("window-size=1920x1080")

                    browser = webdriver.Chrome('chromedriver.exe', options=options)
                    browser.get('https://m.cultureland.co.kr/mmb/loginMain.do')

                    browser.find_element_by_id('txtUserId').send_keys(ID)
                    browser.find_element_by_id('passwd').click()
                    rst = '-'.join(PW).split('-')
                    try:
                        for i in range(0, len(PW)):
                            if rst[i].isdecimal():
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '//img[@alt=\"' + rst[i] + '\"]'))).click()
                            if rst[i].isupper():
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_cp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '//img[@alt=\"대문자' + rst[i] + '\"]'))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_cp\"]/div/img"))).click()
                            if rst[i].islower():
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '//img[@alt=\"' + rst[i] + '\"]'))).click()
                            if rst[i] == '~':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"물결표시\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '@':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"골뱅이\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '$':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"달러기호\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '^':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"꺽쇠\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '*':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"별표\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '(':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"왼쪽괄호\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == ')':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"오른쪽괄호\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '_':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"밑줄\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                            if rst[i] == '+':
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                                WebDriverWait(browser, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, '//img[@alt=\"더하기\"]'))).click()
                                if len(PW) == 12:
                                    pass
                                else:
                                    WebDriverWait(browser, 5).until(
                                        EC.element_to_be_clickable(
                                            (By.XPATH, "//*[@id=\"mtk_sp\"]/div/img"))).click()
                        if len(PW) < 12:
                            WebDriverWait(browser, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//*[@id='mtk_done']/div/img"))).click()
                        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()
                        browser.get('https://m.cultureland.co.kr/csh/cshGiftCard.do')
                    except Exception as e:
                        browser.quit()
                        embed = discord.Embed(title='❌  오류', description='로그인 도중 오류가 발생하였습니다', colour=0xFF0000)
                        await message.channel.send(embed=embed)
                        await client.get_channel(chargelogchannel).send(str(e), embed=embed)
                        return
                    try:
                        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "txtScr11"))).send_keys(
                            pin[0])
                        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "txtScr12"))).send_keys(
                            pin[1])
                        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "txtScr13"))).send_keys(
                            pin[2])

                        lpin = '-'.join(pin[3])
                        lastpin = lpin.split('-')
                        for i in range(0, len(pin[3])):
                            WebDriverWait(browser, 5).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, '//img[@alt=\"' + lastpin[i] + '\"]'))).click()
                        if int(len(pin[3])) == 4:
                            WebDriverWait(browser, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//*[@id=\"mtk_done\"]/div/img"))).click()
                        WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, "btnCshFrom"))).click()
                    except Exception as e:
                        browser.quit()
                        embed = discord.Embed(title='❌  오류', description='충전 도중 오류가 발생하였습니다', colour=0xFF0000)
                        await message.channel.send(embed=embed)
                        await client.get_channel(chargelogchannel).send(str(e), embed=embed)
                        return

                    try:
                        if browser.find_element_by_css_selector(
                                'div.modal.alert[style="z-index: 51; display: block;"]'):
                            browser.quit()
                            embed = discord.Embed(title='❌  오류', description='핀번호가 잘못되었습니다', colour=0xFF0000)
                            await message.channel.send(embed=embed)
                            return
                    except:
                        try:
                            i_result = WebDriverWait(browser, 5).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//*[@id=\"wrap\"]/div[3]/section/div/table/tbody/tr/td[3]/b")))
                            i2_result = i_result.get_attribute('outerHTML')
                            result = i2_result.replace('<b>', '')
                            chresult = result.replace('</b>', '')  # 충전결과

                            i_money = WebDriverWait(browser, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//*[@id=\"wrap\"]/div[3]/section/dl/dd")))
                            i2_money = i_money.get_attribute('outerHTML')
                            money = i2_money.replace('<dd>', '')
                            charge_money = money.replace('</dd>', '')  # 충전금액

                            not_won = charge_money.replace("원", "").replace(',', '')
                        except Exception as e:
                            browser.quit()
                            embed = discord.Embed(title='❌  오류', description='충전결과 수집 도중 오류가 발생하였습니다',
                                                  colour=0xFF0000)
                            await message.channel.send(embed=embed)
                            await client.get_channel(chargelogchannel).send(str(e), embed=embed)
                            return

                        await load.delete()

                        if chresult == '충전 완료':
                            browser.quit()
                            cursor.execute('SELECT money FROM main WHERE user_id = {0}'.format(message.author.id))
                            result = cursor.fetchone()
                            if result == '0':
                                sql = 'UPDATE main SET money = ? WHERE user_id = {0}'.format(message.author.id)
                                pls_money = int(not_won)
                                val = (str(pls_money),)
                                cursor.execute(sql, val)
                                db.commit()
                            else:
                                sql = 'UPDATE main SET money = ? WHERE user_id = {0}'.format(message.author.id)
                                result = str(result)
                                n_money = result.replace('(', '').replace(')', '').replace(',', '').replace("'", "")
                                pls_money = int(n_money) + int(not_won)
                                val = (str(pls_money),)
                                cursor.execute(sql, val)
                                db.commit()

                            cursor.execute('SELECT money FROM main WHERE user_id = {0}'.format(message.author.id))
                            result = cursor.fetchone()
                            result2 = str(result)
                            n_money = result2.replace('(', '').replace(')', '').replace(',', '').replace("'", "")

                            embed = discord.Embed(colour=discord.Colour.green())
                            embed.add_field(name='충전 성공', value='충전금액: {0}'.format(charge_money), inline=False)
                            embed.add_field(name='잔액', value=str(n_money) + '코인', inline=False)
                            print("요청자: {0}, 결과: {1}, 핀번호: {2}, 금액: {3}".format(message.author, chresult, allpin,
                                                                                charge_money))
                            succ = discord.Embed(description='', colour=discord.Colour.green())
                            succ.set_footer(text=f'{message.author} 님 {charge_money} 충전 감사합니다.')
                            await client.get_channel(chargelogchannel).send(embed=succ)

                        else:
                            browser.quit()
                            embed = discord.Embed(color=0xFF0000)
                            embed.add_field(name='충전 실패', value="{0}".format(chresult))
                            print("요청자: {0}, 결과: {1}, 핀번호: {2}".format(message.author, chresult, allpin))
                            fals = discord.Embed(description='', color=discord.Colour.red())
                            fals.set_footer(text=f'{message.author} 님이 충전을 실패하였습니다\n{chresult}')
                            await client.get_channel(chargelogchannel).send(embed=fals)

                        if chresult == '이미 등록된 상품권' or chresult == '상품권 번호 불일치' or chresult == '판매 취소된 문화상품권':
                            await message.channel.send('경고 1회가 부여되었습니다')
                            cursor.execute(
                                'SELECT wrong_pin FROM main WHERE user_id = {0}'.format(message.author.id))
                            count1 = cursor.fetchone()
                            count1 = str(count1)
                            count2 = count1.replace('(', '').replace(')', '').replace(',', '').replace("'", "")

                            sql = 'UPDATE main SET wrong_pin = ? WHERE user_id = {0}'.format(message.author.id)
                            count = int(count2) + 1
                            val = (str(count),)

                            cursor.execute(sql, val)
                            db.commit()
                    await message.channel.send(embed=embed)

                    embed = discord.Embed(description="")
                    embed.set_author(name='10초 후 채널이 삭제됩니다',
                                     icon_url='https://cdn.discordapp.com/attachments/721338948382752810/783923268780032041/aebe49a5b658b59d.gif')
                    await message.channel.send(embed=embed)
                    await asyncio.sleep(10)
                    await message.channel.delete()
                except Exception as e:
                    embed = discord.Embed(title='❌  오류', description='예기치 않은 오류가 발생하였습니다', colour=0xFF0000)
                    await message.channel.send(embed=embed)
                    await client.get_channel(chargelogchannel).send(str(e), embed=embed)
                    return
            else:
                embed = discord.Embed(title='❌  오류', description='올바른 형식의 번호를 입력해주세요', colour=0xFF0000)
                await message.channel.send(embed=embed)


@client.event
async def on_button_click(interaction):
    if interaction.custom_id == "info":
        cursor.execute(f'SELECT user_id FROM main WHERE user_id = {interaction.user.id}')
        result = cursor.fetchone()
        if result is None:
            sql = 'INSERT INTO main(user, user_id, money, wrong_pin) VALUES(?,?,?, ?)'
            val = (str(interaction.author), str(interaction.author.id), str('0'), str('0'))
            cursor.execute(sql, val)
            db.commit()
            with open(f'counting/{interaction.user.id}.txt', 'w') as f:
                f.write('0')

        cursor.execute(f'SELECT money FROM main WHERE user_id = {interaction.user.id}')
        money = cursor.fetchone()
        money = str(money).replace('(', '').replace(')', '').replace(',', '').replace("'", "")

        e = discord.Embed(description='', colour=discord.Colour.blue())
        e.set_footer(text=f'아이디: {interaction.user.id}\n잔액: {money}코인')
        await interaction.respond(content='\n', embed=e)

    if interaction.custom_id == "product":
        with open('name.txt', 'r', encoding='UTF8') as f:
            item_list_forcheck = f.readlines()

        item_list = []

        for t in item_list_forcheck:
            name = str(t).split(";")[0]
            per = str(t).split(";")[1]
            item_list.append(f'**{name}**\n당첨확률: {per}')

        with open('price.txt', 'r') as f:
            price = f.read()
        item_list = '\n'.join(item_list)

        e = discord.Embed(title='💰 상품목록', description=item_list, colour=discord.Colour.blue())
        await interaction.respond(content=f'가격: {price}원', embed=e)

    if interaction.custom_id == "buy":
        cursor.execute(f'SELECT money FROM main WHERE user_id = {interaction.user.id}')
        money = cursor.fetchone()
        if money is None:
            await interaction.respond(content='잔액이 부족합니다')
            return
        money = str(money).replace('(', '').replace(')', '').replace(',', '').replace("'", "")

        before_money = int(money)
        with open('price.txt', 'r', encoding='UTF8') as f:
            item_price = int(f.read())
        after_money = before_money - item_price

        if before_money < item_price:
            await interaction.respond(content='잔액이 부족합니다')
            return

        try:
            dmchecking = await interaction.user.send('구매 진행중입니다..')
        except:
            await interaction.respond(content='디엠발송을 허용해주세요')
            return

        await dmchecking.delete()
        with open('name.txt', 'r', encoding='UTF8') as f:
            item_list_forcheck = f.readlines()

        percentage = []
        item_list = []

        for t in item_list_forcheck:
            name = str(t).split(";")[0]
            p = int(str(t).split(';')[1].replace('%', ''))
            item_list.append(name)
            percentage.append(p)

        choice = random.choices(item_list, weights=percentage)

        sql = f'UPDATE main SET money = ? WHERE user_id = {interaction.author.id}'
        val = (str(after_money),)
        cursor.execute(sql, val)
        db.commit()

        await interaction.respond(content='디엠을 확인해주세요')
        with open(f'counting/{interaction.user.id}.txt', 'r') as f:
            before_count = int(f.read())

        if choice[0] == '꽝':
            with open(f'counting/{interaction.user.id}.txt', 'w') as f:
                f.write(str(before_count + 1))

            e = discord.Embed(description='', colour=discord.Colour.red())
            e.set_footer(text='낙첨되었습니다', icon_url='https://cdn.discordapp.com/attachments/888725597705084949/919410956554084392/Crying_Face_Emoji_grande.png')
            await interaction.user.send(embed=e)
        else:
            with open(f'counting/{interaction.user.id}.txt', 'w') as f:
                f.write('0')
            #random_number = random.randint(0, 16777215)
            #color = int(hex(random_number), 0)
            colors = ['46FFFF', '8572EE', '3DFF92', 'CBFF75', '5CEEE6', '46D2D2', 'FFD4DF', 'FFAAFF', 'FFF56E', '9932CC', 'CE69E7', 'C8D7FF', 'FF64E3']
            inter = int(random.choice(colors), 16)
            color = int(hex(inter), 0)
            e = discord.Embed(description=f'🎉 **{choice[0]}** 에 당첨되셨습니다! 🎉', color=color)
            e.set_author(name=f'{choice[0]} 가 당첨되었습니다!')
            e.set_footer(text=f'당첨되기 전까지 총 {before_count}번의 시도가 있었습니다.')
            e.set_thumbnail(url=client.user.avatar_url)

            e2 = discord.Embed(description=f'🎉 **{interaction.user}** 님이 **{choice[0]}** 에 당첨되셨습니다! 🎉', color=color)
            e2.set_author(name=f'{choice[0]} 가 당첨되었습니다!')
            e2.set_footer(text=f'{interaction.user} 님이 당첨되기 전까지 총 {before_count}번의 시도가 있었습니다.')
            e2.set_thumbnail(url=client.user.avatar_url)
            await interaction.user.send(embed=e)
            await client.get_channel(buylogchannel).send(embed=e2)

    if interaction.custom_id == "charge":
        cursor.execute(f'SELECT user_id FROM main WHERE user_id = {interaction.user.id}')
        result = cursor.fetchone()
        if result is None:
            sql = 'INSERT INTO main(user, user_id, money, wrong_pin) VALUES(?,?,?, ?)'
            val = (str(interaction.author), str(interaction.author.id), str('0'), str('0'))
            cursor.execute(sql, val)
            db.commit()
            with open(f'counting/{interaction.user.id}.txt', 'w') as f:
                f.write('0')

        cursor.execute(f'SELECT wrong_pin FROM main WHERE user_id = {interaction.user.id}')
        wrong = str(cursor.fetchone()).replace('(', '').replace(')', '').replace(',', '').replace("'", "")
        if int(wrong) >= 3:
            await interaction.respond(content='충전횟수 초과로 사용이 차단되었습니다\n관리자에게 문의해주세요')
            return

        if interaction.author.name in str(interaction.guild.channels):
            await interaction.respond(content='이미 충전채널이 존재합니다')
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.author: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                            manage_webhooks=True)
        }

        charge_channel = await interaction.guild.create_text_channel(name=interaction.author.name,
                                                                     overwrites=overwrites, slowmode_delay=100)

        cnl = client.get_channel(int(charge_channel.id))

        embed = discord.Embed(colour=discord.Colour.blue())
        embed.add_field(name='충전방법', value='`!충전 4자리-4자리-4자리-6자리`')
        embed.set_footer(text='※ 일정횟수 이상 충전실패 유발시 자판기 사용 자동차단 / 3분 이내 입력')
        await cnl.send(embed=embed)
        await interaction.respond(content=f'<#{cnl.id}>로 이동해주세요')

        def check(msg):
            return msg.author == interaction.author and msg.channel == cnl

        try:
            await client.wait_for("message", timeout=180, check=check)
        except:
            await cnl.set_permissions(interaction.author, read_messages=True,
                                      send_messages=False)
            embed = discord.Embed(description="")
            embed.set_author(name='5초 후 채널이 삭제됩니다',
                             icon_url='https://cdn.discordapp.com/attachments/721338948382752810/783923268780032041/aebe49a5b658b59d.gif')
            await cnl.send(embed=embed)
            await asyncio.sleep(5)
            await cnl.delete()


client.run(token)
