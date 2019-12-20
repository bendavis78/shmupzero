import random
from animation import ImageAnimation, AnimatedActor

# Settings
WIDTH = 480
HEIGHT = 600
SHIP_SPEED = 10
BULLET_SPEED = 10

# Colors
BLACK = (0, 0, 0)


# Game state variables
class game:
    score = 0
    game_over = False

bullets = []
meteors = []


# Functions
def fire_bullet():
    bullet = Actor('laser', anchor=('center', 'bottom'))
    bullet.y = ship.top
    bullet.x = ship.x
    bullets.append(bullet)


def create_meteor():
    if game.game_over:
        return
    n = random.randint(1, 7)
    meteor = Actor('meteor_' + str(n), anchor=('center', 'center'))
    meteor.y = 0
    meteor.x = random.randint(0, WIDTH)

    # XXX: bad practice (attaching arbitrary properties)
    # Can we realistically get away with this? The only other way to store state on a sprite
    # is to dive into OO.
    meteor.xspeed = random.randint(-500, 500) / 1000
    meteor.yspeed = random.randint(2, 5)
    meteor.explosion = None

    meteors.append(meteor)


#FIXME: is this weird? defining animation first and then using that when creating a sprite?
# The problem is that the ImageAnimation instance can't be re-used. Its frame state is part of the
# animation. It's not a declarative object, but we're kind of using it like one.
#
# Also, we might want to do multiple animations (eg, image anim + rotate + scale). How would that
# look?

def explode_meteor(meteor):
    animation = ImageAnimation('explosion_0{}', 9, 0)
    meteor.explosion = AnimatedActor(animation)
    meteor.explosion.center = meteor.center
    meteor.explosion.animation.play()


def explode_ship():
    animation = ImageAnimation('sonic_explosion_0{}', 9, 0)
    ship.explosion = AnimatedActor(animation)
    ship.explosion.center = ship.center
    ship.explosion.animation.play()


def update_ship():
    # Remove the ship explosion when the animation is done playing
    if ship.explosion and ship.explosion.animation.is_ended():
        ship.explosion = None

    if game.game_over:
        return

    # Ship movement
    if not ship.explosion and keyboard.left:
        ship.x -= SHIP_SPEED
    if not ship.explosion and keyboard.right:
        ship.x += SHIP_SPEED

    # constrain to proportions
    if ship.left < 0:
        ship.left = 0
    if ship.right >= WIDTH:
        ship.right = WIDTH

    # Fire bullet if space is pressed but not already firing
    if keyboard.space:
        if not ship.firing:
            fire_bullet()
        ship.firing = True
    else:
        ship.firing = False


def update_bullets():
    # Update bullet positions
    for bullet in bullets:
        bullet.y -= BULLET_SPEED
        if bullet.y < 0:
            bullets.remove(bullet)


def update_meteors():
    if game.game_over:
        return

    for meteor in meteors:
        # Update meteor positions
        if not meteor.explosion:
            meteor.x += meteor.xspeed
            meteor.y += meteor.yspeed
        
            # Check if meteors collide with ship (assuming we're not exploding)
            if not ship.explosion and meteor.colliderect(ship):
                explode_ship()

            # Check if meteor collides with a bullet
            for bullet in bullets:
                if meteor.colliderect(bullet):
                    explode_meteor(meteor)
        else:
            # remove the meteor when it's done exploding
            if meteor.explosion.animation.is_ended():
                meteors.remove(meteor)

# Create the ship
ship = Actor('ship', anchor=('center', 'bottom'))
ship.bottom = HEIGHT - 10
ship.x = WIDTH / 2
ship.explosion = None

# create a meteor every second
clock.schedule_interval(create_meteor, 1)


def update():
    update_ship()
    update_bullets()
    update_meteors()


def draw():
    screen.fill(BLACK)
    screen.blit('starfield', (0, 0))

    if game.game_over:
        return

    for meteor in meteors:
        if meteor.explosion:
            meteor.explosion.draw()
        else:
            meteor.draw()

    for bullet in bullets:
        bullet.draw()

    if ship.explosion:
        ship.explosion.draw()
    else:
        ship.draw()
